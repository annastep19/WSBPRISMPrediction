from scipy.linalg import block_diag
from utils import *
from fluxes import *
from oscProbs import *


class flux_fitter:
    """
    Define and calculate everuthing for DUNE-PRISM flux matching

    Methods:
        -- __init__(): load energy and OA ranges, probability, nominal and shifted fluxes
            -- load_nom() -> load_FD_nom(), 
                             load_ND_nom() 
            -- load_shifts() -> load_FD_other_shifts(), 
                                load_ND_other_shifts(), 
                                load_FD_ppfx_shifts(), 
                                load_ND_ppfx_shifts()
        -- add_new_FD(): load new FD flux as a target
        -- set_fit_region(): a fit region to match
        -- set_OOR(): out of range weights 
        -- set_cutOArange(): reload fluxes in new OA range
        -- calc_coeffs(): calculate coeffs and return target, LC, coeffs
    """

    def __init__(self, oscParam = None, 
                       file_set = False, 
                       useHC = False, 
                       Erebin = False, OArebin = False, 
                       other_loaded = False, ppfx_loaded = False, **kwargs):
        """
        Args:
            -- oscParam (class): use oscillation probability or not
            -- file_set (str): name od data file (see fluxes.py)
            -- useHC (bool): use HC in ND off-axis matrix to match or not
            -- Erebin (int) / OArebin (int): rebin E/OA bins
            -- other_loaded/ppfx_loaded (bool): load other/ppfx shifts or not
            -- **kwargs: PpfxUniv (int): 1...100
        """

        self.f = file_set

        ## from fluxes.py
        # set E range
        self.Ebins = Ebins[self.f]  # central values of energy
        self.EbinEdges = EbinEdges[self.f]

        # set OA range
        self.__OAbins = OAbins[self.f] # central values of OA positions
        self.__OAbinEdges = OAbinEdges[self.f]
        if self.__OAbinEdges[0] < 0:
           print("WARNING! Using the OA position less than 0 m")
        
        # rebin E range
        if Erebin: 
            self.Ebins = average(self.Ebins, Erebin)
            self.EbinEdges = self.EbinEdges[::Erebin]

        # rebin OA range
        if OArebin:
            self.__OAbins = average(self.__OAbins, OArebin)
            self.__OAbinEdges = self.__OAbinEdges[::OArebin]

        # using a full OA range. It might be changed in set_OArange().
        self.cut_OArange_flag = False 
        self.OABins = self.__OAbins
        self.OAEdges = self.__OAbinEdges

        # use an additional HC
        self.useHC = useHC
        if not self.useHC:
            self.HC_nom = None

        # if not specified, load the default oscillation profile
        if oscParam == "no_osc":
            # the probability of 1 along all bins
            self.Posc = np.array([1]*len(self.Ebins)) 
        else:
            self.oscParam = oscParam
            self.Posc = self.oscParam.load(self.Ebins)

        # load nominal fluxes
        self.load_nom()

        # load shifted fluxes 
        self.ppfx_loaded = ppfx_loaded
        self.other_loaded = other_loaded
        self.load_shifts(**kwargs)

        # set default bounds for the fit
        self.Ebounds = (0, Ebins[self.f][-1])
        self.OutOfRegionFactors = (0, 0)

        # are changed after set self.add_new_FD()
        self.FD_RHC_nom = None
        self.FD_RHC_shifts = None

    def load_FD_nom(self):
        """
        load nominal 1D FD flux  
        """

        self.FD_nom = FD_nominal[self.f].load(binEdges = [self.EbinEdges])

    def load_ND_nom(self):
        """
        load nominal 2D ND flux for off-axis positions at 300(293) kA,
        *load nominal additional 1D HC and add it to 2D ND flux*
        """

        self.ND_nom = ND_nominal[self.f].load(binEdges = [self.EbinEdges, self.OAEdges])

        if self.useHC:
            self.HC_nom = HC_nominal[self.f].load(binEdges = [self.EbinEdges])
            self.ND_HC_nom = np.append(self.ND_nom.T, [self.HC_nom], axis=0).T

    def load_nom(self):
        """
        load all nominal fluxes
        """

        self.load_FD_nom()
        self.load_ND_nom()

    def load_FD_other_shifts(self):
        """
        load other shifted 1D FD flux for each shift
        """

        FD_other = {key: shift.load(binEdges = [self.EbinEdges])
              for key, shift in FD_other_shifts[self.f].items()}
        self.FD_other_shifts = FD_other   
        
    def load_ND_other_shifts(self):
        """
        load other shifted 2D ND flux for each shift
        *load other shifted additional 1D HC and add it to 2D ND flux for each shift*
        """

        ND_other = {key: shift.load(binEdges = [self.EbinEdges, self.OAEdges])
                          for key, shift in ND_other_shifts[self.f].items()}
        self.ND_other_shifts = ND_other

        if self.useHC:
            HC_other = {key: shift.load(binEdges = [self.EbinEdges])
                  for key, shift in HC_other_shifts[self.f].items()}
            self.HC_other_shifts = HC_other  

            ND_other = {key: np.append(self.ND_other_shifts[key].T, [self.HC_other_shifts[key]], axis=0).T
                             for key in ND_other_shifts[self.f].keys()}
            self.ND_other_shifts = ND_other

    def load_FD_ppfx_shifts(self):
        """
        load ppfx shifted 1D FD flux for CV and each univ
        and normalize it on nominal 1D FD flux
        """

        nUniv = self.nPpfxUniv

        if self.f == 'old':
           name = 'old'
        else:
           # WARNING: because there are no new ppfx fluxes we use old ones in both cases
           name = 'old'

        FD_CV = FD_ppfx_CV[name].load(binEdges = [self.EbinEdges])
        FD_ppfx = np.array([shift.load(binEdges = [self.EbinEdges])
                                        for shift in FD_ppfx_univ[name][:nUniv]])
        FD_ppfx /= FD_CV
        FD_ppfx *= self.FD_nom
            
        self.FD_ppfx_shifts = FD_ppfx

    def load_ND_ppfx_shifts(self):
        """
        load ppfx shifted 2D ND flux for CV and each univ 
        and normalize it on nominal 2D ND flux
        *load ppfx shifted additional 1D HC and add it to 2D ND flux for CV and each univ
        and normalize it on nominal 2D ND flux*
        """

        if self.f == 'old':
           name = 'old'
        else:
           # WARNING: because there are no new ppfx fluxes we use old ones in both cases
           name = 'old'

        nUniv = self.nPpfxUniv
        ND_CV = ND_ppfx_CV[name].load(binEdges = [self.EbinEdges, self.OAEdges])
        ND_ppfx = np.array([shift.load(binEdges = [self.EbinEdges, self.OAEdges])
                                        for shift in ND_ppfx_univ[name][:nUniv]])
        ND_ppfx /= ND_CV
        ND_ppfx *= self.ND_nom

        self.ND_ppfx_shifts = ND_ppfx

        if self.useHC:
            HC_CV = HC_ppfx_CV[name].load(binEdges = [self.EbinEdges])
            HC_ppfx = np.array([shift.load(binEdges = [self.EbinEdges])
                                            for shift in HC_ppfx_univ[name][:nUniv]])
            HC_ppfx /= HC_CV
            HC_ppfx *= self.HC_nom

            self.HC_ppfx_shifts = HC_ppfx

            ND_ppfx = np.array([np.append(self.ND_ppfx_shifts[i].T, [self.HC_ppfx_shifts[i]], axis=0).T for i in range(0, nUniv)])
            self.ND_ppfx_shifts = ND_ppfx

    def load_shifts(self, **kwargs):
        """
        load all systematic shifted fluxes
        """

        if self.ppfx_loaded:
            self.nPpfxUniv = kwargs['PpfxUniv']
            self.load_FD_ppfx_shifts()
            self.load_ND_ppfx_shifts()
       
        if self.other_loaded:
            self.load_FD_other_shifts()
            self.load_ND_other_shifts()

    def add_new_FD(self):
        """
        load the new nominal far detector flux and update the FD_oscillated;
        load new systematic throw fluxes for specific beam parameters for the far detector
        """

        self.FD_RHC_nom = FD_RHC_nom[self.f].load(binEdges = [self.EbinEdges])

        if self.other_loaded:
            FD_RHC_other = {key: shift.load(binEdges = [self.EbinEdges])
                              for key, shift in FD_RHC_other_shifts[self.f].items()}
            self.FD_RHC_other_shifts = FD_RHC_other

        if self.f == 'old':
           name = 'old'
        else:
           # WARNING: because there are no new ppfx fluxes we use old ones in both cases
           name = 'old'

        if self.ppfx_loaded:
            nUniv = self.nPpfxUniv
            FD_RHC_CV = FD_RHC_ppfx_CV[name].load(binEdges = [self.EbinEdges])
            FD_RHC_ppfx = np.array([shift.load(binEdges = [self.EbinEdges])
                                            for shift in FD_RHC_ppfx_univ[name][:nUniv]])
            FD_RHC_ppfx /= FD_RHC_CV
            FD_RHC_ppfx *= self.FD_RHC_nom

            self.FD_RHC_ppfx_shifts = FD_RHC_ppfx


    def set_fit_region(self, energies: list):
        """
        Specify the energy region in which to fit the ND and target fluxes. 
        
        Args:
          energies (list): might be tuple
        """

        assert len(energies) == 2, "Energy bounds must be length 2!"
        self.Ebounds = energies

    def set_OOR(self, weights: list):
        """
        Specify the weights of the regions outside of the "fit region"
        when contributing to the residual. 

        Args:
          weights (list): might be tuple
        """

        assert len(weights) == 2, "Weights outside the fit region must be length 2!"
        self.OutOfRegionFactors = weights


    def cut_OArange(self, OA_range):
        """
        Specify OA range smaller than full OA range. 
        self.__OAbinEdges_new and __self.OAbinEdges are different 
        in order to call cut_OArange many times in one class object.

        Args:
            OA_range(list): might be tuple
        """ 

        assert len(OA_range) == 2, "OA_range must be length 2!"
        self.minOA = OA_range[0]
        self.maxOA = OA_range[-1]

        OA_condition_left = self.__OAbins >= self.minOA
        OA_condition_right = self.__OAbins <= self.maxOA
        self.__OAbins_new = self.__OAbins[OA_condition_left & OA_condition_right]

        extended_mask_left = np.pad(OA_condition_left, (0,1), 'edge')
        extended_mask_right = np.pad(OA_condition_right, (1,0), 'edge')
        self.__OAbinEdges_new = self.__OAbinEdges[extended_mask_left & extended_mask_right]

        self.cut_OArange_flag = True
        self.OABins = self.__OAbins_new
        self.OAEdges = self.__OAbinEdges_new
        self.load_ND_nom()

        if self.ppfx_loaded:
            self.load_ND_ppfx_shifts()

        if self.other_loaded:
            self.load_ND_other_shifts()


    def calc_coeffs(self, reg, FD_init, useHC=True):
        """
        Calculate coefficients of linear combination of 
        ND off-axis fluxes to predict FD flux
        """

        if useHC:
            useHC = self.useHC

        if useHC:
            ND = self.ND_HC_nom
        else:
            ND = self.ND_nom
        target = FD_init * self.Posc        

        # penalty matrix A
        nBinsOA = len(self.OABins)
        OA_penalty = np.diag((nBinsOA-1)*[1] + [0]) - np.diag((nBinsOA - 1)*[1], k = 1)
        if useHC:
            HC_penalty = np.diag([0])
            A = block_diag(OA_penalty, HC_penalty)
        else:
            A = block_diag(OA_penalty)

        self.A = A
        Gamma = reg * self.A
        self.Gamma = Gamma

        # weighting matrix for target flux
        P = np.diag(np.where(self.Ebins > self.Ebounds[1], self.OutOfRegionFactors[1],
                    np.where(self.Ebins < self.Ebounds[0], self.OutOfRegionFactors[0], 1)))
        self.P = P

        # ND matrix
        NDmatr = np.matrix(ND)

        if reg == 0:
            LHS = NDmatr.T # left-hand side
            RHS = target   # right-hand side
        else:
            LHS = np.matmul(NDmatr.T, np.matmul(P, NDmatr)) + np.matmul(Gamma.T, Gamma)
            RHS = np.dot(np.matmul(NDmatr.T, P), target)
        
        self.c = np.array(np.dot(RHS, LHS.I)).squeeze()

        self.fluxPred = np.array(np.dot(ND, self.c))
       
        self.target = target
        return self.target, self.fluxPred, self.c
