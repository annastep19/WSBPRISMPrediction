import matplotlib.pyplot as plt
import os
import numpy as np

def plot_nom_fluxes_coeff(reg, fitter, type_target=False, 
                          woHC=False, reg_wo=False, ratio=True):
        """
        Plot nominal LC and FD fluxes

        Args:
            reg (float): a reg parameter
            fitter (object): class object
            type_target (str): FHC/RHC
            woHC (bool): plot additional curves w/o the lower HC in LC 
            reg_wo (float): a reg parameter for them 
            ratio (bool): plot ratio of DUNE-PRISM LC flux and FD flux or not
        """

        colors = {"orange": "#F19E54", 
                  "blue": "#7FAED5"}

        def _axis_style(ax, fit_range=True):
            ax.yaxis.get_major_formatter().set_useMathText(True)
            if fit_range:
                ax.axvline(Ebounds[0], color='red', linestyle='dashed', alpha=0.6)
                ax.axvline(Ebounds[1], color='red', linestyle='dashed', alpha=0.6)
            ax.grid(which='both', color = 'grey')
            ax.legend(fontsize=11)  

        file_set = fitter.f
        Energy = fitter.Ebins
        EnergyEdges = fitter.EbinEdges
        OAbins = fitter.OABins
        OAEdges = fitter.OAEdges

        Ebounds = fitter.Ebounds

        if type_target == 'FHC':
            FD_unosc = fitter.FD_nom
        elif type_target == 'RHC':
            FD_unosc = fitter.FD_RHC_nom 

        if woHC:
            # calculate coeffs for w/o HC
            target_wo, fluxPred_wo, coeff_wo = fitter.calc_coeffs(reg_wo, FD_unosc, useHC=False)   
            attrib_wo = ("PRISM off-axis", colors["blue"])     
    
        # calculate coeffs
        target, fluxPred, c = fitter.calc_coeffs(reg, FD_unosc)
        coeff = c[:-1]
        attrib = ("PRISM+HC", colors["orange"])

        y_units = r"$\Phi, \nu \mathrm{s} / \mathrm{cm^2} / \mathrm{POT} / \mathrm{GeV}$"

        if ratio:
            fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(nrows=2, ncols=2, figsize=(12, 7))
        else:
            fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2, figsize=(10, 3))

        ax0.plot(Energy, target, label="$\mathrm{FD_{osc}}$", color='black')
        if woHC:
            ax0.plot(Energy, fluxPred_wo, label=attrib_wo[0], color=attrib_wo[1])
            ax1.step(OAbins, coeff_wo, where="mid",
                             label=attrib_wo[0], color=attrib_wo[1])
            if ratio:
                ax2.plot(Energy, (fluxPred_wo - target)/FD_unosc, 
                              label=attrib_wo[0], color=attrib_wo[1])

        ax0.plot(Energy, fluxPred,label=attrib[0], color=attrib[1])
        ax0.set_title(r"Flux comparison")
        ax0.set_ylabel(y_units, fontsize=11)
        ax0.set_xlabel(r"$\mathrm{E_{\nu}}$, GeV", fontsize=11)
        ax0.set_xlim(EnergyEdges[0], EnergyEdges[-1])

        ax1.step(OAbins, coeff, where="mid", label=attrib[0], color=attrib[1])
        ax1.set_xlabel("Off-axis position, m", fontsize=11)
        ax1.set_xlim(OAEdges[0], OAEdges[-1])
        ax1.set_ylabel(r"$\mathrm{C_i}$",fontsize=11)
        ax1.set_title("Coefficients")

        if ratio:
            ax2.plot(Energy, (fluxPred-target)/FD_unosc, label=attrib[0], color=attrib[1])
            ax2.set_ylabel(r"$\frac{\mathrm{ND_{PRISM} - FD_{osc}}}{\mathrm{FD_{unosc}}}$", fontsize=14)
            ax2.set_ylim(-0.5, 0.5)
            ax2.set_title("Ratio")
            ax2.set_xlabel(r"$\mathrm{E_{\nu}}$, GeV", fontsize=11) 
            ax2.set_xlim(EnergyEdges[0], EnergyEdges[-1])
            _axis_style(ax2)

        _axis_style(ax0)
        _axis_style(ax1, fit_range=False)

        if file_set == 'old':
            f_s = "OLD"
            lamb = r'$\lambda = 5$ x $10^{-9}$'
        else:
            f_s = 'NEW'
            lamb = r'$\lambda = 4$ x $10^{-9}$'
    
        if ratio:
            ax3.set_axis_off()
            ax3.text(0.2, 0.8, 'Fluxes:  ' + f_s, fontsize=14)
            ax3.text(0.2, 0.65, r'Target: $\nu_{\mu}$ ' + type_target, fontsize=14)
            ax3.text(0.2, 0.4, lamb, fontsize=13)

        plt.tight_layout()

        if file_set == 'old':
            file_set = 'Old'
        else:
            file_set = 'New'

        dir_plt = os.path.join("images", file_set) 
        if not os.path.isdir(dir_plt):
            os.mkdir(dir_plt)

        path_name = os.path.join(dir_plt, type_target + "_nom_coeff.pdf")
        plt.savefig(path_name)
        print(f"Saved in {path_name}")
