from FormFile import FormFile

class BaseCombine:
    """ add fluxes in root-file of mode. 

    Methods:
        -- __init__(): define mode parameters
        -- nom_fluxes(): add nominal ND (neutrino), FD (any), HC (neutrino) fluxes 
                         (for old fluxes)
        -- ppfx_fluxes(): add ppfx ND (neutrino), FD (any), HC (neutrino) fluxes
                         (for old fluxes)
        -- other_fluxes(): add other ND (neutrino), FD (any), HC (neutrino) fluxes
                         (for old fluxes)
    """
    def __init__(self, params):
        self.params = params   

    def _combine_fluxes_(self, suffix, input_fluxes, add_HCs):
        """
        Args:
            suffix (str): part of name of output ND/FD hists
            input_other (dict): ND/FD/HC fluxes
            add_HCs (func): particular type of function for HCs
        """
        mode_file = FormFile(**self.params['FormFile_PARAM'])

        if self.params['mode'] == 'neutrino':
            mode_file.add("ND", "ND_" + suffix, "2D", input_fluxes['ND_hist'])

        mode_file.add("FD", "FD_" + suffix, "1D", input_fluxes['FD_hist'])
        mode_file.close()

        if self.params['mode'] == 'neutrino':
            # it is necessary to open again
            mode_file_HC = FormFile(**self.params['FormFile_PARAM'])
            add_HCs(mode_file_HC, input_fluxes['HC_params'])

            mode_file_HC.close()

    
    def nom_fluxes(self, input_nom):
        """
        Args:
            input_other (dict): ND/FD/HC fluxes
        """
        suffix = "NominalFlux"

        changing = lambda x, y: x.add(*y)
        input_nom['HC_params'] = ("ND", "Additional_HC", "1D", input_nom['HC_hist'])
        self._combine_fluxes_(suffix, input_nom, changing)


    def ppfx_fluxes(self, throw, input_ppfx):
        """
        Args:
            throw (str): CV or number between 0 and 99
            input_other (dict): ND/FD/HC fluxes
        """
        suffix = "ppfx_" + throw

        changing = lambda x, y: x.add(*y)
        input_ppfx['HC_params'] = ("ND", "HC_" + suffix, "1D", input_ppfx['HC_hist'])
        self._combine_fluxes_(suffix, input_ppfx, changing)


    def other_fluxes(self, shift, sigma_type, input_other):
        """
        Args:
            shifts (str): DPR, WL, ...
            sigma_type (str): p1 / m1
            input_other (dict): ND/FD/HC fluxes
        """
        if sigma_type == 'p1': 
            sigma_name = 'pos'
        elif sigma_type == 'm1':
            sigma_name = 'neg'
        else:
            raise Exception('p1 or m1')

        suffix = shift + "_" + sigma_name + "_1_sigma"

        changing = lambda x, y: x.HC_other_old(*y)
        input_other['HC_params'] = ("ND", "HC_" + suffix, input_other['HC_hist'])
        self._combine_fluxes_(suffix, input_other, changing)
