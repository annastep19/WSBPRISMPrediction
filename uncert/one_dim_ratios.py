from ROOT import TFile
import os
import one_dim_utils

# calculate ND flux ratios of nominal and shifted fluxes at a particular position 
if 'N_FLUX_FILE' in os.environ:
    neutrino_flux_file = os.environ['N_FLUX_FILE']
else:
    neutrino_flux_file = "neutrino_branches.root"

if 'AN_FLUX_FILE' in os.environ:
    antineutrino_flux_file = os.environ['AN_FLUX_FILE']
else:
    antineutrino_flux_file = "antineutrino_branches.root"


neutrino_branches = TFile(neutrino_flux_file)
antineutrino_branches = TFile(antineutrino_flux_file)

D = ("LAr center", "LAr_center")
loc_pos = [0, 10]
uncert_types = {"R decay pipe": "DecayPipeRadius_pos_1_sigma_neutrino_",
                "Horn current": "HornCurrent_pos_1_sigma_neutrino_", 
                "Water thickness": "HornWaterLayerThickness_pos_1_sigma_neutrino_", 
                "Proton beam radius": "ProtonBeamRadius_pos_1_sigma_neutrino_"}

for loc in loc_pos:
    # return list of nominal fluxes: [FHC, RHC]
    nom = one_dim_utils.nominal_flux(neutrino_branches, antineutrino_branches, loc, "OfficialEngDesignSept2021_neutrino_"+D[1])
    for UT in uncert_types.keys():
        # return list of one type shifted fluxes: [FHC+, FHC-, RHC+, RHC-]  
        current_uncert = one_dim_utils.one_uncert(neutrino_branches, antineutrino_branches, loc, uncert_types[UT]+D[1])
        # return energy range, ratios and create plots
        ratios = one_dim_utils.two_ratios(nom, current_uncert, UT, loc, D[0])

neutrino_branches.Close()
antineutrino_branches.Close()
