from ROOT import TFile
import os

def choose_file(shift_name):
    """
    Used Pierce's files: 
      -- nominal flux: OfficialEngDesignSept2021_neutrino_LAr_center.root
      -- shifted fluxes: (DecayPipeRadius)_neg(pos)_1_sigma_(anti)neutrino_LAr_center.root
    
    
    Extracts hist "Unosc_numu_flux_DUNEPRISM_LAr_center" and renames as the initial file. 
    Saves here as "(anti)neutrino_branches.root"

    """

    for neutrino in ["neutrino", "antineutrino"]:
        for how in ["pos", "neg"]:
            # should be local directories "neutrino/" and "antineutrino/"
            neutrino_flux_path = os.path.join("/home/anna/mywork/prism/project", neutrino)
            dot = ".root"
            branch_name = "Unosc_numu_flux_DUNEPRISM_LAr_center"

            new_name = shift_name.replace('neutrino', neutrino)
            new_name = new_name.replace('neg', how)
            neutrino_branches = TFile(os.path.join(neutrino_flux_path, new_name+dot))
            TH = neutrino_branches.Get(branch_name)

            output_hist = TFile(neutrino + "_branches" + dot, "update")
            TH.Write(new_name, option=2)

            output_hist.Close()
            neutrino_branches.Close()


if __name__ == "__main__":
    nom = "OfficialEngDesignSept2021_neutrino_LAr_center"

    rest_part = "_neg_1_sigma_neutrino_LAr_center"
    DP = "DecayPipeRadius"
    HC = "HornCurrent"
    HW = "HornWaterLayerThickness"
    PB = "ProtonBeamRadius"

    choose_file(nom)
    choose_file(DP + rest_part)
    choose_file(HC + rest_part)
    choose_file(HW + rest_part)
    choose_file(PB + rest_part)
