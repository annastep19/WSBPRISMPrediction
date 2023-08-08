from ROOT import *
import os
import numpy as np
gROOT.SetBatch(True)


def cut_hists(hist, title, ERange=[0.5, 8], LocRange=[-4, 30]):
    """
    extract an initial hist, cut x and y axes, return new hist
    """

    TAX = hist.GetXaxis()
    TAY = hist.GetYaxis()
    TAZ = hist.GetZaxis()

    xMinBin = TAX.FindBin(ERange[0])
    xMaxBin = TAX.FindBin(ERange[1])
    xBins = xMaxBin - xMinBin

    yMinBin = TAY.FindBin(LocRange[0])
    yMaxBin = TAY.FindBin(LocRange[1])
    yBins = yMaxBin - yMinBin

    shape = [xBins, yBins]
    flux = np.ndarray(shape)
    err = np.ndarray(shape)
    energy = np.ndarray(shape[0])
    loc = np.ndarray(shape[1])
    
    cut_hist = TH2D(title, title, shape[0], ERange[0], ERange[1], 
                                  shape[1], LocRange[0], LocRange[1])

    for j, yNum in enumerate(range(yMinBin, yMaxBin)):
        for i, xNum in enumerate(range(xMinBin, xMaxBin)):
            energy[i] = TAX.GetBinCenter(xNum)
            loc[j] = TAY.GetBinCenter(yNum)
            flux[i,j] = hist.GetBinContent(xNum, yNum)
            cut_hist.Fill(energy[i], loc[j], flux[i,j])

    yLabel = TAY.GetTitle()
    zLabel = TAZ.GetTitle()
    cut_hist.GetYaxis().SetTitle(yLabel)

    xLabel = TAX.GetTitle()
    cut_hist.GetXaxis().SetTitle(xLabel)
    return cut_hist

def TwoDimRatios(nom, sigma, nom_bar, sigma_bar, detector, uncert, sign_type):
    """
    plot 2D ratios of nominal and shifted numu fluxes: in FHC (signal), in RHC (bkg) 
    """

    if sign_type == "pos":
        sign = "+"
    elif sign_type == "neg":
        sign = "-"

    nom_reb = nom.Clone()
    sigma_reb = sigma.Clone()
    nom_reb.Rebin2D(30, 10)
    sigma_reb.Rebin2D(30, 10)
    
    nom_bar_reb = nom_bar.Clone()
    sigma_bar_reb = sigma_bar.Clone()
    nom_bar_reb.Rebin2D(30, 10)
    sigma_bar_reb.Rebin2D(30, 10)
    
    c1 = TCanvas()

    gStyle.SetPalette(kRainBow)   
    c1.Divide(2,2)
    ratio = sigma_reb.Clone()
    ratio.SetStats(0)
    ratio.SetTitle("#nu_{#mu} FHC ratio: sigma/nominal")
    ratio.Divide(nom_reb)
    c1.cd(1)
    ratio.Draw("COLZ")

    ratio_bar = sigma_bar_reb.Clone()
    ratio_bar.SetStats(0)
    ratio_bar.SetTitle("#nu_{#mu} RHC ratio: sigma/nominal")
    ratio_bar.Divide(nom_bar_reb)
    c1.cd(2)
    ratio_bar.Draw("COLZ")

    double_ratio = ratio.Clone()
    double_ratio.SetStats(0)
    double_ratio.SetTitle("Double ratio: #nu_{#mu} FHC ratio / #nu_{#mu} RHC ratio")
    double_ratio.Divide(ratio_bar)
    c1.cd(3)
    double_ratio.Draw("COLZ")

    c1.cd(4)
    tex = TLatex(0.3,0.7,"#splitline{"+detector+"}{" +uncert+" "+sign+" 1#sigma}")
    tex.SetNDC()
    tex.SetTextSize(0.06)
    tex.Draw()

    zMin = ratio.GetMinimum()
    zMax = ratio.GetMaximum()
    zMin1 = ratio_bar.GetMinimum()
    zMax1 = ratio_bar.GetMaximum()
    zMin2 = double_ratio.GetMinimum()
    zMax2 = double_ratio.GetMaximum()
    zMinim = [zMin, zMin1, zMin2]
    zMaxim = [zMax, zMax1, zMax2]
    zSmall = min(zMinim)
    zBig = max(zMaxim)
    ratio.SetAxisRange(zSmall, zBig, "Z");
    ratio_bar.SetAxisRange(zSmall, zBig, "Z");
    double_ratio.SetAxisRange(zSmall, zBig, "Z");

    dir_plt = "imgs/twodim/"
    if not os.path.isdir(dir_plt):
        os.mkdir(dir_plt)
    c1.SaveAs(dir_plt + detector + " " + uncert + " " + sign_type + ".pdf")


if __name__ == "__main__":

    neutrino = ["neutrino", "antineutrino"]
    neutrino_flux_file = neutrino[0] + "_branches.root"
    antineutrino_flux_file = neutrino[1] + "_branches.root"

    D = ("LAr center", "LAr_center")
    signs = ['pos', 'neg']
    uncert_types = {"Decay Pipe Radius": "DecayPipeRadius_pos_1_sigma_",
                    "Horn Current": "HornCurrent_pos_1_sigma_",
                    "Horn Water Layer Thickness": "HornWaterLayerThickness_pos_1_sigma_", 
                    "Proton Beam Radius": "ProtonBeamRadius_pos_1_sigma_"}

    # open two mode files
    neutrino_branches = TFile(neutrino_flux_file)
    antineutrino_branches = TFile(antineutrino_flux_file)

    # extract nominal hist
    nom = neutrino_branches.Get("OfficialEngDesignSept2021_"+neutrino[0]+"_"+D[1])
    nom_bar = antineutrino_branches.Get("OfficialEngDesignSept2021_"+neutrino[1]+"_"+D[1])

    # cut them
    nom_cut = cut_hists(nom, 'nomin')
    nom_cut_bar = cut_hists(nom_bar, 'nomin_bar')

    for sign in signs:
        for UT in uncert_types.keys():
            uncert_types[UT] = uncert_types[UT].replace("pos", sign) 
            # extract shifted hists 
            sigma = neutrino_branches.Get(uncert_types[UT]+neutrino[0]+"_"+D[1])
            sigma_bar = antineutrino_branches.Get(uncert_types[UT]+neutrino[1]+"_"+D[1])
            # cut them
            sigma_cut = cut_hists(sigma, UT+sign+neutrino[0])
            sigma_cut_bar = cut_hists(sigma_bar, UT+sign+neutrino[1])
            # plot 2D ratios
            TwoDimRatios(nom_cut, sigma_cut, nom_cut_bar, sigma_cut_bar, D[0], UT, sign)

    neutrino_branches.Close()
    antineutrino_branches.Close()
