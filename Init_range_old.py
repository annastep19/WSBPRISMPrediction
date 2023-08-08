from FormFile import FormFile
from BaseCombine import BaseCombine


class Combine_old(BaseCombine):
    """inherit from BaseCombine
    """
    def __init__(self, params):
        super().__init__(params)

def main():
    mode_param = dict(neutrino=('nu', '_Nom', "_HC_280"),
                      antineutrino=('nubar', '', "_HC280"))
    for mode in mode_param.keys():
        flavor = mode_param[mode][0]
        Nom_280 = mode_param[mode][1]
        last_part = mode_param[mode][2]

        FormFile_PARAM = dict(output_file="outputs/" + mode + "_range_old.root", 
                              cut=True, ERange=[0., 8.], LocRange=[0, 33])
        params = dict(mode=mode, FormFile_PARAM=FormFile_PARAM)
        base_file = BaseCombine(params)

        # nominal fluxes
        input_nom = dict(
          ND_hist=('all_HC.root', "ND_" + flavor + "_ppfx/LBNF_numu_flux_Nom"),
          FD_hist=('all_HC.root', "FD_" + flavor + "_ppfx/LBNF_numu_flux_Nom"),
          HC_hist=('all_HC.root', "ND_" + flavor + last_part + "/LBNF_numu_flux" + Nom_280))

        base_file.nom_fluxes(input_nom)

        # ppfx fluxes
        def set_input_ppfx(throw_name):
            input_ppfx = dict(
              ND_hist=('all_HC.root', "ND_" + flavor + "_ppfx/LBNF_numu_flux_" + throw_name),
              FD_hist=('all_HC.root', "FD_" + flavor + "_ppfx/LBNF_numu_flux_" + throw_name),
              HC_hist=('all_HC.root', "ND_" + flavor + last_part + "/LBNF_numu_flux_" + throw_name))
            return input_ppfx

        throw_name = 'CV'
        input_ppfx = set_input_ppfx(throw_name)
        base_file.ppfx_fluxes(throw_name, input_ppfx)
        N = 100
        for number in range(0, N):
            throw_name = 'univ_' + str(number)
            input_ppfx = set_input_ppfx(throw_name)
            base_file.ppfx_fluxes(str(number), input_ppfx)
            if number == N-1:
                print(f"ppfx for {mode} mode are done")


        # other shifts
        def set_input_other(shift, sigma_type):
            old_hist_name = flavor + "_" + shift + "_" + sigma_type + "/LBNF_numu_flux"
            input_other = dict(
              ND_hist=('all_HC.root', "ND_" + old_hist_name),
              FD_hist=('all_HC.root', "FD_" + old_hist_name),
              HC_hist=(('all_HC.root', "ND_" + old_hist_name),
                       ('all_HC.root', "ND_" + flavor + "_ppfx/LBNF_numu_flux_Nom"),
                       ('all_HC.root', "ND_" + flavor + last_part + "/LBNF_numu_flux" + Nom_280)))
            return input_other


        shifts = ['DPR', 'WL', 'HC']
        p1 = 'p1'

        shifts_also = ['TargetDensity']
        m1 = 'm1'

        for shift in shifts:
            input_other = set_input_other(shift, p1)
            base_file.other_fluxes(shift, p1, input_other)

        for shift in shifts_also:
            input_other = set_input_other(shift, m1)
            base_file.other_fluxes(shift, m1, input_other)

if __name__ == "__main__":
    main()
