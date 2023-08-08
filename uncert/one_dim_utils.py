from ROOT import *
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import os


def EnergyFlux(yLoc, infile, branch_name, ERange=[0.5, 8]):
    """
    rebin y axis and cut x axis
    """

    TH_fine = infile.Get(branch_name)
    TH = TH_fine.Clone()
    TH.Rebin2D(50, 1)
    
    TAX = TH.GetXaxis()
    TAY = TH.GetYaxis()
    yLocBin = TAY.FindBin(yLoc)
    xMin = TAX.FindBin(ERange[0])
    xMax = TAX.FindBin(ERange[1])
    
    shape = TH.GetNbinsX()
    energy = np.ndarray(shape)
    flux = np.ndarray(shape)
    err = np.ndarray(shape)

    for i in range(shape):
        energy[i] = TAX.GetBinLowEdge(i+1)
        flux[i] = TH.GetBinContent(i+1, yLocBin)
        err[i] = TH.GetBinError(i+1, yLocBin)
    return energy[xMin:xMax-1], flux[xMin:xMax-1], err[xMin:xMax-1]

def nominal_flux(neutrino_branches, antineutrino_branches, loc, branch_name):
    """
    load nominal fluxes for neutrino and antineutrino modes
    """

    branch_name_bar = branch_name.replace('neutrino', 'antineutrino')

    nominal = EnergyFlux(loc, neutrino_branches, branch_name)
    nominal_bar = EnergyFlux(loc, antineutrino_branches, branch_name_bar)
    
    return nominal, nominal_bar

def one_uncert(neutrino_branches, antineutrino_branches, loc, branch_name_pos):
    """
    load shifted fluxes for neutrino and antineutrino modes
    """

    branch_name_neg = branch_name_pos.replace('pos', 'neg')
    branch_name_pos_bar = branch_name_pos.replace('neutrino', 'antineutrino')
    branch_name_neg_bar = branch_name_pos.replace('pos', 'neg').replace('neutrino', 'antineutrino')
    pos_sigma = EnergyFlux(loc, neutrino_branches, branch_name_pos)
    neg_sigma = EnergyFlux(loc, neutrino_branches, branch_name_neg)
    pos_sigma_bar = EnergyFlux(loc, antineutrino_branches, branch_name_pos_bar)
    neg_sigma_bar = EnergyFlux(loc, antineutrino_branches, branch_name_neg_bar)
    
    return pos_sigma, neg_sigma, pos_sigma_bar, neg_sigma_bar

def two_ratios(nomin, unsert, uncert_name, position, detector, plots=True):
    """
    calculate ratios of nominal and shifted fluxes at a patricular off-axis position 

    Args:
    -- plots (bool): if True it saves plots with double ratios of FHC and RHC ratios
        
    """
    def yerrors(sigma, nominal, sigma_err, nominal_err):
        return sigma/nominal * np.sqrt(sigma_err**2/sigma**2 + nominal_err**2/nominal**2) 

    x = nomin[0][0]
    
    nominal = nomin[0][1]
    nominal_bar = nomin[1][1]
    pos_sigma = unsert[0][1]
    neg_sigma = unsert[1][1]
    pos_sigma_bar = unsert[2][1]
    neg_sigma_bar = unsert[3][1]
    
    nominal_err = nomin[0][2]
    nominal_bar_err = nomin[1][2]
    pos_sigma_err = unsert[0][2]
    neg_sigma_err = unsert[1][2]
    pos_sigma_bar_err = unsert[2][2]
    neg_sigma_bar_err = unsert[3][2]
    
    
    ratio_pos = pos_sigma/nominal
    ratio_neg = neg_sigma/nominal
    ratio_pos_bar = pos_sigma_bar/nominal_bar
    ratio_neg_bar = neg_sigma_bar/nominal_bar       
    
    
    ratio_neg_err = yerrors(neg_sigma, nominal, neg_sigma_err, nominal_err)
    ratio_neg_bar_err = yerrors(neg_sigma_bar, nominal_bar, neg_sigma_bar_err, nominal_bar_err)
    ratio_pos_err = yerrors(pos_sigma, nominal, pos_sigma_err, nominal_err)
    ratio_pos_bar_err = yerrors(pos_sigma_bar, nominal_bar, pos_sigma_bar_err, nominal_bar_err)
    
    if plots:
        if position == 0:
            name_loc = "OnAxis: "
        else:
            name_loc = "OffAxis: "
    
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
        fig.suptitle(detector+", "+uncert_name+", "+name_loc+str(position)+" m ", fontsize=20)
        
        def style_fluxes(ax):
            ax.set_ylabel(r'$\nu_{\mu}$s/POT', fontsize=22)
            formatter = ax.yaxis.get_major_formatter()
            formatter.set_powerlimits((-4, 4))
            formatter.set_useMathText(True)
            ax.yaxis.get_offset_text().set_fontsize(16)
            ax.legend(fontsize=16)
            ax.tick_params(labelsize=16) 
            ax.set_ylim(0, )
            ax.set_xlim(0.5, 8.)
            ax.grid(which='major', color = 'grey')  

        def style_ratio(ax, max_value, min_value, v="bottom"):
            ax.set_xlim(0.5, 8.)
            if ((max_value - 1.05) > 0 or (min_value - 0.95) < 0):
                ax.set_ylim(0.9,1.1)
                if v=="up":
                    ax.set_yticks([0.9, 1., 1.1])
                else:
                    ax.set_yticks([0.9, 1.,])
            else:
                ax.set_ylim(0.95,1.05)
                if v=="up":
                    ax.set_yticks([0.95, 1., 1.05])
                else:
                    ax.set_yticks([0.95, 1.,])


            ax.tick_params(axis='y', labelsize=16)
            ax.tick_params(axis='x', labelsize=1)      
            ax.grid(which='major', color = 'grey')  
            
        def last_bin(ax, y, line_color):
            ax.hlines(y[-1], x[-1], 2*x[-1]-x[-2], color=line_color, linewidth=4)
            
        
        neutr_max = np.max(nominal)*9/10
        ax[0].text(3.8, neutr_max, r"$\nu_{\mu}$, FHC", fontsize=22)
        ax[0].errorbar(x, nominal, yerr=nominal_err, fmt='o', capsize=5, 
                         label="$N_{nom}$ : nominal flux", color = "darkgreen", linewidth=4)
        ax[0].errorbar(x, pos_sigma, yerr=pos_sigma_err, fmt='o',  capsize=5, 
                         label=r"$N_{+\sigma} : $"+uncert_name+r" $+ \ \sigma$", color = "darkblue", linewidth=4)
        ax[0].errorbar(x, neg_sigma, yerr=neg_sigma_err, fmt='o', capsize=5, 
                         label=r"$N_{-\sigma} : $"+uncert_name+r" $- \ \sigma$", color = "cornflowerblue", linewidth=4)
        style_fluxes(ax[0])
        ax[0].set_xlabel("E, GeV", fontsize=22)

        antineutr_max = np.max(nominal_bar)*9/10
        ax[1].text(3.8, antineutr_max, r"$\nu_{\mu}$, RHC", fontsize=22)
        ax[1].errorbar(x, nominal_bar, yerr=nominal_bar_err, fmt='o', capsize=5,
                         label="$N_{nom}$ : nominal flux", color = "darkgreen", linewidth=4)
        ax[1].errorbar(x, pos_sigma_bar, yerr=pos_sigma_bar_err, fmt='o', capsize=5,
                         label=r"$N_{+\sigma}$ : "+uncert_name+r" $+ \ \sigma$", color = "brown", linewidth=4)
        ax[1].errorbar(x, neg_sigma_bar, yerr=neg_sigma_bar_err, fmt='o', capsize=5,
                         label="$N_{-\sigma}$ : "+uncert_name+r" $- \ \sigma$", color = "darkorange", linewidth=4)
        style_fluxes(ax[1])
        ax[1].set_xlabel("E, GeV", fontsize=22)
        plt.tight_layout()

        fig_r, axr = plt.subplots(nrows=2, ncols=2, figsize=(20, 8))
        fig_r.suptitle("Ratios between nominal and $\pm \sigma$ fluxes. Double ratios", fontsize=22)

        # ratio left up
        ratio_pos_max = np.max(ratio_pos)
        ratio_pos_min = np.min(ratio_pos)
        axr[0,0].errorbar(x, ratio_pos, color="darkblue", linewidth=4, 
                          yerr=ratio_pos_err, fmt='o', capsize=5, label=r"${\nu}_{\mu}$, FHC")
        axr[0,0].errorbar(x, ratio_pos_bar, color="brown", linewidth=4, yerr=ratio_pos_bar_err, fmt='o', capsize=5,
                     alpha=0.8, label=r"$\nu_{\mu}$, RHC")
        axr[0,0].set_title(r'$R^+_{i} = N_{+\sigma, i}/N_{nom, i}$, $i=\{\nu_{\mu}, \mathrm{FHC}, \ \nu_{\mu}, \mathrm{RHC}\}$', fontsize=22)
        axr[0,0].set_ylabel(r'$R^+_{i}$', fontsize=22)
        axr[0,0].legend(fontsize=16)
        style_ratio(axr[0,0], ratio_pos_max, ratio_pos_min, "up")

        #ratio left up
        ratio_neg_max = np.max(ratio_neg)
        ratio_neg_min = np.min(ratio_neg)
        axr[0,1].errorbar(x, ratio_neg, color="cornflowerblue",  linewidth=4,
                          yerr=ratio_neg_err, fmt='o', capsize=5,
                     label=r"${\nu}_{\mu}$, FHC")
        axr[0,1].errorbar(x, ratio_neg_bar, color="darkorange",  linewidth=4,
                          yerr=ratio_neg_bar_err, fmt='o', capsize=5,
                     label=r"$\nu_{\mu}$, RHC")
        axr[0,1].set_title(r'$R^-_{i} = N_{-\sigma, i}/N_{nom, i}$, $i=\{\nu_{\mu}, \mathrm{FHC}, \ \nu_{\mu}, \mathrm{RHC}\}$', fontsize=22)
        axr[0,1].set_ylabel(r'$R^-_{i}$', fontsize=22)
        axr[0,1].legend(fontsize=16)
        style_ratio(axr[0,1], ratio_neg_max, ratio_neg_min, "up")
        
        # double ratio left 
        double_ratio_pos = ratio_pos/ratio_pos_bar
        double_ratio_pos_max = np.max(double_ratio_pos)
        double_ratio_pos_min = np.min(double_ratio_pos)
        axr[1,0].errorbar(x, double_ratio_pos, color="red", linewidth=4,  
                         yerr=yerrors(ratio_pos, ratio_pos_bar, ratio_pos_err, ratio_pos_bar_err),  
                         fmt='o', capsize=5)
        axr[1,0].set_ylabel(r'$R^+_{\nu_{\mu}, \mathrm{FHC}}/R^+_{\nu_{\mu}, \mathrm{RHC}}$', fontsize=22)
        style_ratio(axr[1,0], double_ratio_pos_max, double_ratio_pos_min)     
        axr[1,0].tick_params(axis='x', labelsize=16)      
        axr[1,0].set_xlabel("E, GeV", fontsize=22)

        
        # double ratio right
        double_ratio_neg = ratio_neg/ratio_neg_bar
        double_ratio_neg_max = np.max(double_ratio_neg)
        double_ratio_neg_min = np.min(double_ratio_neg)
        axr[1,1].errorbar(x, double_ratio_neg, color="black", linewidth=4, 
                          yerr=yerrors(ratio_neg, ratio_pos_bar, ratio_pos_err, ratio_pos_bar_err), 
                          fmt='o', capsize=5)
        axr[1,1].set_ylabel(r'$R^-_{\nu_{\mu}, \mathrm{FHC}}/R^-_{\nu_{\mu}, \mathrm{RHC}}$', fontsize=22)
        axr[1,1].set_xlabel("E, GeV", fontsize=22)
        style_ratio(axr[1,1], double_ratio_neg_max, double_ratio_neg_min)
        axr[1,1].tick_params(axis='x', labelsize=16)      
        plt.tight_layout()
        fig_r.subplots_adjust(hspace=0)

        dir_plt = "imgs/onedim/"
        if not os.path.isdir(dir_plt):
            os.mkdir(dir_plt)

        imgfile = PdfPages(dir_plt+detector+", "+uncert_name+", "+name_loc+str(position)+" m.pdf")
        
        imgfile.savefig(fig, facecolor="white")
        imgfile.savefig(fig_r, facecolor="white")
        
        imgfile.close()
    return  x, ratio_pos, ratio_neg, ratio_pos_bar, ratio_neg_bar
