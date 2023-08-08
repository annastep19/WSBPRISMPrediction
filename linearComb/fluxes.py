from utils import *
from ROOT import TFile

class flux:
    """ define fluxes for using in flux_fitter

    Methods:
        -- _init_(): define a file and a hist name
        -- define_dict(): create dict of 'flux' class objects, where 
                          keys are names of different data
        -- define_doule_dict(): create dict in dict, where 
                                keys1 are names of different data,
                                keys2 are names of different shifts
        -- define_list_in_dict(): create list in dict, where 
                                  keys are names of different data,
                                  list is made of numbered fluxes
        -- load(): is used in class 'flux_fitter' to load fluxes
    """
    def __init__(self, infileName, branchName):
        self.infileName = infileName
        self.branchName = branchName

    def define_dict(self, NewOld: list):
        """
        Args:
            NewOld (list): names of initial data files 
        """
        return {key: flux(self.infileName + key + ".root", self.branchName) 
                for key in NewOld}

    def define_double_dict(self, systematics: dict):
        """
        Args:
            NewOld (dict): keys -- names of initial data files, values -- names of shifts 
        """
        return {key: {syst: flux(self.infileName + key + ".root", 
                                 self.branchName + syst + "_1_sigma") 
                      for syst in set_systs} 
                for key, set_systs in systematics.items()}

    def define_list_in_dict(self, NewOld: list, N):
        """
        Args:
            NewOld (list): names of initial data files,
            N (int): 1...100
        """
        return {key: [flux(self.infileName + key + ".root",
                           self.branchName + str(i)) for i in range(N)] 
                for key in NewOld}


    def load(self, **kwargs):
        """
        load a hist 

        Returns:
            content (array): 1D or 2D array from the hist
        """
        infile = TFile(self.infileName)
        TH = infile.Get(self.branchName)
        assert TH != None, f"{self.branchName} doesn't exist in {self.infileName}"
        content = root_to_array(TH, **kwargs)
        infile.Close()
        return content


input_path = "../outputs/"
mode = "neutrino"
mode_RHC = "antineutrino"
rest_name = "_range_"

NewOld = ["300_285", "old"]

file_name = input_path + mode + rest_name
file_name_RHC = input_path + mode_RHC + rest_name

ppfx_N = 100
systematics = {"300_285" : ("HornCurrent_pos", 
                         "DecayPipeRadius_pos", 
                         "HornCurrent_neg", 
                         "DecayPipeRadius_neg", 
                         "HornWaterLayerThickness_pos",
                         "HornWaterLayerThickness_neg",
                         "ProtonBeamRadius_pos",
                         "ProtonBeamRadius_neg"), 
               "old" : ('DPR_pos', 
                        'WL_pos',
                        'HC_pos',   
                        'TargetDensity_neg')}

ND_nominal = flux(file_name, "ND/ND_NominalFlux").define_dict(NewOld)
HC_nominal = flux(file_name, "ND/Additional_HC").define_dict(NewOld)

ND_other_shifts = flux(file_name, "ND/ND_").define_double_dict(systematics)
HC_other_shifts = flux(file_name, "ND/HC_").define_double_dict(systematics)

ND_ppfx_CV = flux(file_name, "ND/ND_ppfx_CV").define_dict(NewOld)
HC_ppfx_CV = flux(file_name, "ND/HC_ppfx_CV").define_dict(NewOld)

ND_ppfx_univ = flux(file_name, "ND/ND_ppfx_").define_list_in_dict(NewOld, ppfx_N)
HC_ppfx_univ = flux(file_name, "ND/HC_ppfx_").define_list_in_dict(NewOld, ppfx_N)


FD_nominal = flux(file_name, "FD/FD_NominalFlux").define_dict(NewOld)
FD_other_shifts = flux(file_name, "FD/FD_").define_double_dict(systematics)
FD_ppfx_CV = flux(file_name, "FD/FD_ppfx_CV").define_dict(NewOld)
FD_ppfx_univ = flux(file_name, "FD/FD_ppfx_").define_list_in_dict(NewOld, ppfx_N)


FD_RHC_nom = flux(file_name_RHC, "FD/FD_NominalFlux").define_dict(NewOld)
FD_RHC_other_shifts = flux(file_name_RHC, "FD/FD_").define_double_dict(systematics)
FD_RHC_ppfx_CV = flux(file_name_RHC, "FD/FD_ppfx_CV").define_dict(NewOld)
FD_RHC_ppfx_univ = flux(file_name_RHC, "FD/FD_ppfx_").define_list_in_dict(NewOld, ppfx_N)


nomFile, nomTH, Ebins, OAbins = {}, {}, {}, {}
EbinLowEdges, OAbinLowEdges, EbinUpEdges, OAbinUpEdges = {}, {}, {}, {}
EbinEdges, OAbinEdges = {}, {}
for key in NewOld:
    nomFile[key]= TFile(file_name + key + ".root")
    nomTH[key] = nomFile[key].Get("ND/ND_NominalFlux")
    Ebins[key] = root_to_axes(nomTH[key])[0]
    OAbins[key] = root_to_axes(nomTH[key])[1]

    EbinLowEdges[key] = root_to_axes(nomTH[key], where='pre')[0]
    OAbinLowEdges[key] = root_to_axes(nomTH[key], where='pre')[1]
    EbinUpEdges[key] = root_to_axes(nomTH[key], where='post')[0]
    OAbinUpEdges[key] = root_to_axes(nomTH[key], where='post')[1]

    EbinEdges[key] = np.concatenate([EbinLowEdges[key], EbinUpEdges[key][-1:]])
    OAbinEdges[key] = np.concatenate([OAbinLowEdges[key], OAbinUpEdges[key][-1:]])
