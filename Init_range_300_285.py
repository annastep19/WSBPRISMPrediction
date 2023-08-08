from FormFile import FormFile
from BaseCombine import BaseCombine
import os

class Combine_300_285(BaseCombine):
    """inherit from BaseCombine
    
    Methods:
       other_fluxes(): x.HC_other_old -> x.HC_other_new 
                       (change other_fluxes() from BaseCombine)
    """
    def __init__(self, params):
        super().__init__(params)

    def other_fluxes(self, shift, sigma_type, input_other):
        suffix = shift + "_" + sigma_type + "_1_sigma"

        changing = lambda x, y: x.HC_other_new(*y)
        input_other['HC_params'] = ("ND", "HC_" + suffix, "1D", input_other['HC_hist'])
        self._combine_fluxes_(suffix, input_other, changing)

def main():
    mode_param = dict(neutrino=('nu',), antineutrino=('nubar',))          
    for mode in mode_param.keys():
        flavor = mode_param[mode][0]

        FormFile_PARAM = dict(output_file="outputs/" + mode + "_range_300_285.root", 
                              cut=True, ERange=[0., 8.], LocRange=[0, 33],
                              DivWidthGeV=True, scale=0.0001, add_bin=1)
        params = dict(mode=mode, FormFile_PARAM=FormFile_PARAM)
        com_file = Combine_300_285(params)

        # nominal fluxes
        nominal_file_name = os.path.join(mode, "OfficialEngDesignSept2021_" + mode)
        nom_HC_file_name = os.path.join(mode, "HornCurrent285kAforPRISM_nominal_" + mode + "_finemc.root")
        input_nom = dict(
            ND_hist=(nominal_file_name + "_LAr_center.root",          
                     "Unosc_numu_flux_DUNEPRISM_LAr_center"),
            FD_hist=(nominal_file_name + "_finemc.root", "Unosc_flux_numu_finemc_DUNEFD"),
            HC_hist=(nom_HC_file_name, "Unosc_flux_numu_finemc_DUNEND"))

        com_file.nom_fluxes(input_nom)

        # ppfx fluxes: see linearComb/flux_fitter.py -> 
        #                  load_FD_ppfx_shifts()/load_ND_ppfx_shifts()

        # other shifts
        def set_input_other(shift, sigma_type):
            shift_hist = shift + "_" + sigma_type + "_1_sigma"
            other_file_name = os.path.join(mode, shift_hist + "_" + mode)
            input_other = dict(
              ND_hist=(other_file_name + "_LAr_center.root",
                             "Unosc_numu_flux_DUNEPRISM_LAr_center"),
              FD_hist=(other_file_name + "_finemc.root", "Unosc_flux_numu_finemc_DUNEFD"),
              HC_hist=((os.path.join(mode, shift_hist + "_" + mode + "_finemc.root"),
                        "Unosc_flux_numu_finemc_DUNEND"),
                       (os.path.join(mode, "OfficialEngDesignSept2021_" + mode + "_finemc.root"),
                         "Unosc_flux_numu_finemc_DUNEND"),
                       (os.path.join(mode, "HornCurrent285kAforPRISM_nominal_" + mode + "_finemc.root"),
                         "Unosc_flux_numu_finemc_DUNEND")))
            return input_other

        shifts = ['DecayPipeRadius', 'HornWaterLayerThickness', 'HornCurrent', 'ProtonBeamRadius']
        sigma_types = ['pos', 'neg']

        for shift in shifts:
            for sigma_type in sigma_types:
                input_other = set_input_other(shift, sigma_type)
                com_file.other_fluxes(shift, sigma_type, input_other)

if __name__ == "__main__":
    main()

