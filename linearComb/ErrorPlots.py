import matplotlib.pyplot as plt
import os
import utils
import numpy as np


class ErrorPlots:
    """ 
    Make plots of ppfx/other shifts for FHC/RHC target and old/new fluxes

    Methods:
        -- __init()__: load class object 'fitter', energy range, bins, bounds, probability,
                       choose new/old data
        -- shifted_plots(): plot and save as pdf page consisted of 6 figures
            -- extract_fluxes()
            -- add_nom_fluxes()
            -- add_other_set()
            -- add_ppfx_set()
            -- axis_style()
            -- fit_lines()
            -- save()
    """
    def __init__(self, fitter):
        self.fitter = fitter
        self.file_set = fitter.f
        self.Energy = fitter.Ebins
        self.EnergyEdges = fitter.EbinEdges
        self.Posc = self.fitter.Posc

        # draw fit region
        self.min_Ebound = fitter.Ebounds[0]
        self.max_Ebound = fitter.Ebounds[1]

    def shifted_plots(self, type_target, reg, type_shifts, 
                            Nreb=False, ylim_F=False, ylim_R=[0,0,0]):
        """
        Plot and save as pdf page consisted of 6 figures

        Funs:
          -- extract_fluxes(): return target, PRISM LC, coeffs as arrays
          -- add_nom_fluxes(): plot FD unosc, FD osc, ND PRISM fluxes
          -- add_other_set(): plot figures associated with other shifts
          -- add_ppfx_set(): plot figures associated with ppfx shifts
          -- axis_style(): set axis style
          -- fit_lines(): draw vertical red lines separated the fit range 
              
        Args:
            type_target (str: FHC/RHC): type of target
            reg (float): value of optimal lambda
            type_shifts (str: other/ppfx): type of shifts
            Nreb (int): rebin for add_other_set()
            ylim_F (float): y lim for flux plots
            ylim_R (list): y lim for ratio plots
        """

        target, fluxPred, c = self.extract_fluxes(type_target, reg, type_shifts)
        self.target, self.fluxPred, self.c = target, fluxPred, c

        self.fig, ((ax0, ax1, ax2), (ax3, ax4, ax5)) = plt.subplots(figsize=(16, 9), 
                                                                  nrows=2, ncols=3)
        if type_shifts == 'other':
            title = 'Focusing'
        else:
            title = 'PPFX'

        if self.file_set == 'old':
            f_s = "OLD"
        else:
            f_s = 'NEW'

        plt.suptitle(title + ' uncertainies', fontsize=16)
        ax5.text(0.1, 0.9, 'Fluxes:  ' + f_s, fontsize=16)
        ax5.text(0.1, 0.8, r'Target: $\nu_{\mu}$ ' + type_target, fontsize=16)

        self.add_nom_fluxes(ax3)
        if type_shifts == 'other':
            self.add_other_set(ax0, ax1, ax2, ax4, ax5, type_shifts, Nreb)
        if type_shifts == 'ppfx':
            self.add_ppfx_set(ax0, ax1, ax2, ax4, ax5, type_shifts)

        self.fit_lines(ax0)
        self.fit_lines(ax1)
        self.fit_lines(ax2)
        self.fit_lines(ax3)
        self.fit_lines(ax4)

        self.axis_style(ax0, type_shifts, 'ND', ylim_R=ylim_R[0])
        self.axis_style(ax1, type_shifts, 'FD', ylim_R=ylim_R[1])
        self.axis_style(ax2, type_shifts, 'both', ylim_R=ylim_R[2])
        self.axis_style(ax3, type_shifts, 'nom', ylim_F=ylim_F)
        self.axis_style(ax4, type_shifts, 'shifts', ylim_F=ylim_F)

        self.save(type_target, type_shifts)

    def extract_fluxes(self, type_target, reg, type_shifts):
        """
        Extract fluxes from 'self.fitter' object

        Args:
            -- type_target (str): FHC/RHC
            -- reg (float): a reg parameter
            -- type_shifts (str): other/ppfx
        """
        if type_target == 'FHC':
            self.FD_nom = self.fitter.FD_nom
            if type_shifts == 'other':
                self.FD_shifts = self.fitter.FD_other_shifts
            elif type_shifts == 'ppfx':
                self.FD_shifts = self.fitter.FD_ppfx_shifts
        elif type_target == 'RHC':
            self.fitter.add_new_FD()
            self.FD_nom = self.fitter.FD_RHC_nom
            if type_shifts == 'other':
                self.FD_shifts = self.fitter.FD_RHC_other_shifts
            elif type_shifts == 'ppfx':
                self.FD_shifts = self.fitter.FD_RHC_ppfx_shifts
        else:
            raise Exception(f'Type of target is FHC/RHC, not {type_target}')

        if type_shifts == 'other':
            self.ND_shifts = self.fitter.ND_other_shifts
            self.list_of_shifts = self.FD_shifts.keys()
        elif type_shifts == 'ppfx':
            self.ND_shifts = self.fitter.ND_ppfx_shifts
            self.list_of_shifts = range(0, self.fitter.nPpfxUniv)
        else:
            raise Exception(f"Type of uncertainties is other/ppfx, not {type_others}")

        target, fluxPred, c = self.fitter.calc_coeffs(reg, self.FD_nom)
        return target, fluxPred, c

    def add_nom_fluxes(self, ax):
        """
        Plot FD unosc, FD osc, ND PRISM fluxes
        """

        ax.plot(self.Energy, self.FD_nom, label="$\mathrm{FD_{unosc}}$",
                                          color='darkmagenta', linestyle='dashed')
        ax.plot(self.Energy, self.target, label="$\mathrm{FD_{osc}}$", color="black")
        ax.plot(self.Energy, self.fluxPred, label="$\mathrm{ND_{PRISM}}$", color="magenta")


    def add_other_set(self, ax0, ax1, ax2, ax4, ax5, type_shifts, Nreb):
        """
        Plot figures associated with other shifts
    
        Funcs:
            -- _add_shifted_fluxes()
            -- _add_ratio() <- __r_c() 
            -- _ax5_legend()

        Args:
            ax0, ax1, ax2, ax4, ax5 (axis): figures with other shifts
            type_shifts (str): other
            Nreb (int): N for rebin 
        """

        def _add_shifted_fluxes(ax, shift, number_of_shift):
            # add shifted flux in the figure
            ax.plot(self.Energy, np.dot(self.ND_shifts[shift], self.c),
                                 label=str(number_of_shift))

        def _add_ratio(ax, flux_type, shift, number_of_shift):
            """
            Add ratios

            Args:
                flux_type (str): ND/FD/both
                shift (str): HornCurrent/DecayPipe/...
                number_of_shift (int): 1, 2, ...
            """

            def __r_c(tp):
                """
                Return *rebined* ratio: 
                            x = (ND shift * c - FD osc)/FD unosc 
                            or y = ((FD shift * P osc) - FD osc)/FD unosc
                            or z = x - y                            
                Args:
                    tp (str): ND/FD/both 
                """

                if tp == "ND":
                    x = (np.dot(self.ND_shifts[shift], self.c) - self.fluxPred)/self.FD_nom
                    return utils.average(x, Nreb) if Nreb else x
                elif tp == "FD":
                    x = (self.FD_shifts[shift] * self.Posc - self.target)/self.FD_nom
                    return utils.average(x, Nreb) if Nreb else x
                elif tp == 'both':
                    x = (np.dot(self.ND_shifts[shift], self.c) - self.fluxPred)/self.FD_nom
                    y = (self.FD_shifts[shift] * self.Posc - self.target)/self.FD_nom
                    z = x - y
                    return utils.average(z, Nreb) if Nreb else z
                else: 
                    raise Exception("type of flux: FD/ND/both")

            ratio = __r_c(flux_type)
            Energy_R = utils.average(self.Energy, Nreb) if Nreb else self.Energy
            linewidth = 2
            a = ax.step(Energy_R, ratio, label=str(number_of_shift), where='mid',
                        linewidth=linewidth)
            color = a[0].get_color()
            width = (Energy_R[0] + Energy_R[1])/2
            ax.hlines(ratio[0], Energy_R[0] - width, Energy_R[0], 
                      color=color, linewidth=linewidth)
            ax.hlines(ratio[-1], Energy_R[-1], Energy_R[-1] + width, 
                      color=color, linewidth=linewidth)
            return color

        def _ax5_legend(ax, type_shifts, shift, number_of_shift, color):
            # add text in figure 5
            if 'pos' in shift:
                self.shift_label = str(number_of_shift) + ' ' + shift.split('_pos')[0] + r' $+1 \sigma$'
            elif 'neg' in shift:
                self.shift_label = str(number_of_shift) + ' ' + shift.split('_neg')[0] + r' $-1 \sigma$'
            ax.set_axis_off()
            ax.text(-0.1, 0.7 - 0.1 * number_of_shift, self.shift_label, fontsize=14, color=color)

        number_of_shift = 0
        for shift in self.list_of_shifts:
            number_of_shift += 1
            _add_shifted_fluxes(ax4, shift, number_of_shift)
            _add_ratio(ax0, 'ND', shift, number_of_shift)
            _add_ratio(ax1, 'FD', shift, number_of_shift)
            color = _add_ratio(ax2, 'both', shift, number_of_shift)
            _ax5_legend(ax5, type_shifts, shift, number_of_shift, color)


    def add_ppfx_set(self, ax0, ax1, ax2, ax4, ax5, type_shifts):
        """
        Plot figures associated with ppfx shifts

        Funcs:
            -- _add_shifted_fluxes()
            -- _add_sigma_range() <- __r_c() 
            -- _ax5_legend()

        Args:
            ax0, ax1, ax2, ax4, ax5 (axis): figures with ppfx shifts
            type_shifts (str): ppfx
            Nreb (int): N for rebin 
        """

        def _add_shifted_fluxes(ax):
            # add shifted flux in the figure. There is 68% flux band (1 sigma).
            x = np.array([np.dot(self.ND_shifts[shift], self.c) for shift in self.list_of_shifts])
            mean_x = np.mean(x, axis=0)
            min_x = np.min(x, axis=0)
            max_x = np.max(x, axis=0)
            min_x_68 = mean_x - (mean_x - min_x) * 0.34
            max_x_68 = (max_x - mean_x) * 0.34 + mean_x
            ax.plot(self.Energy, mean_x, color='tab:blue')
            ax.fill_between(self.Energy, min_x_68, max_x_68, color='tab:blue', alpha=0.6)
    
        def _add_sigma_range(ax, flux_type):
            """
            Add ratios in 1 sigma band

            Args:
                flux_type (str): ND/FD/both
            """
            def __r_c(tp):
                """ return *rebined* ratio: 
                            x = (ND shift * c - FD osc)/FD unosc * 0.68
                            or y = ((FD shift * P osc) - FD osc)/FD unosc * 0.68
                            or z = x - y 

                Args:
                    tp (str): ND/FD/both 
                """

                if tp == 'ND':
                    x = np.array([np.dot(self.ND_shifts[shift], self.c) for shift in self.list_of_shifts])
                    mean_x = np.mean(x, axis=0)
                    min_x = np.min(x, axis=0)
                    max_x = np.max(x, axis=0)

                    mean_r = (mean_x - self.fluxPred)/self.FD_nom
                    min_r = (min_x - self.fluxPred)/self.FD_nom
                    max_r = (max_x - self.fluxPred)/self.FD_nom
                    
                    min_r_68 = 0.34 * min_r 
                    max_r_68 = 0.34 * max_r

                    return mean_r, min_r_68, max_r_68
                elif tp == 'FD':
                    x = np.array([(self.FD_shifts[shift] * self.Posc) for shift in self.list_of_shifts])
                    mean_x = np.mean(x, axis=0)
                    min_x = np.min(x, axis=0)
                    max_x = np.max(x, axis=0)

                    mean_r = (mean_x - self.target)/self.FD_nom
                    min_r = (min_x - self.target)/self.FD_nom
                    max_r = (max_x - self.target)/self.FD_nom

                    min_r_68 = 0.34 * min_r 
                    max_r_68 = 0.34 * max_r

                    return mean_r, min_r_68, max_r_68
                elif tp == 'both':
                    x = np.array([np.dot(self.ND_shifts[shift], self.c) for shift in self.list_of_shifts])
                    y = np.array([(self.FD_shifts[shift] * self.Posc) for shift in self.list_of_shifts])
                    z = x - y
                    mean_z = np.mean(z, axis=0)
                    min_z = np.min(z, axis=0)
                    max_z = np.max(z, axis=0)   
     
                    mean_r = (mean_z - self.fluxPred + self.target)/self.FD_nom
                    min_r = (min_z - self.fluxPred + self.target)/self.FD_nom
                    max_r = (max_z - self.fluxPred + self.target)/self.FD_nom

                    min_r_68 = 0.34 * min_r 
                    max_r_68 = 0.34 * max_r

                    return mean_r, min_r_68, max_r_68

            ppfx_ratio = __r_c(flux_type)
            ax.plot(self.Energy, ppfx_ratio[0], color='tab:blue')
            ax.fill_between(self.Energy, ppfx_ratio[1], ppfx_ratio[2], color='tab:blue', alpha=0.6)

        def _ax5_legend(ax):
            # add text in figure 5
            shift_label = r'$1 \sigma$' +  f" band for {self.fitter.nPpfxUniv} PPFX throws"

            ax.set_axis_off()
            ax.text(-0.1, 0.5, shift_label, fontsize=16)

        _add_sigma_range(ax0, "ND")
        _add_sigma_range(ax1, "FD")
        _add_sigma_range(ax2, "both")
        _add_shifted_fluxes(ax4)
        _ax5_legend(ax5)


    def axis_style(self, ax, type_shifts, ax_type, 
                         ylim_F=False, ylim_R=False, xlabel=True):
        """
        Set axis style

        Args:
            type_shifts (str): other/ppfx
            ax_type (str): nom/shifts/ND/FD/both
            ylim_F (float): y limit for flux plot
            ylim_R (list, dim=3): y limit for ratio plots
            xlabel (bool): set or not x label 
        """

        F_size = 14
        R_size = 14

        if not xlabel:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel(r"$\mathrm{E_{\nu}}$, GeV", fontsize=F_size)
        
        if ax_type == 'nom':
            ylabel = r"$\Phi, \nu \mathrm{s} / \mathrm{cm^2} / \mathrm{POT} / \mathrm{GeV}$"
            ax.set_title("Nominal fluxes", fontsize=F_size)
        elif ax_type == 'shifts':
            ylabel = r"$\Phi, \nu \mathrm{s} / \mathrm{cm^2} / \mathrm{POT} / \mathrm{GeV}$"
            ax.set_title("Shifted $\mathrm{ND_{PRISM}}$ fluxes", fontsize=F_size)

        elif ax_type == 'ND':
            ylabel = "$\dfrac{\mathrm{{ND}^{shift}}-\mathrm{ND^{nom}}}{\mathrm{FD_{unosc}}}$"
            ax.set_title(r"$\mathrm{ND_{PRISM}}$ ratios", fontsize=R_size)
        elif ax_type == 'FD':
            ylabel = "$\dfrac{\mathrm{{FD}^{shift}}-\mathrm{FD^{nom}}}{\mathrm{FD_{unosc}}}$"
            ax.set_title("FD ratios", fontsize=R_size)
        elif ax_type == 'both':
            ylabel = "$\dfrac{((\mathrm{{ND}^{shift}}-\mathrm{ND^{nom}}) - (\mathrm{{FD}^{shift}}-\mathrm{FD^{nom}}))}{\mathrm{FD_{unosc}}}$"
            ax.set_title("Both ratios", fontsize=R_size)

        ax.set_ylabel(ylabel, fontsize=F_size if (ax_type == 'nom' or ax_type == 'shifts') else R_size)
            
        if ylim_R:
            ax.set_ylim(-ylim_R, ylim_R)

        if ylim_F:
            ax.set_ylim(0, ylim_F)

        ax.tick_params(labelsize=11)
        ax.set_xlim(self.EnergyEdges[0], self.EnergyEdges[-1]) 
        ax.grid(which='both', color = 'grey')  
        ax.yaxis.get_major_formatter().set_useMathText(True)
        if type_shifts == 'other':
            ax.legend(fontsize=9)


    def fit_lines(self, ax):
        # draw vertical red lines separated the fit range 
        ax.axvline(self.min_Ebound, color='red', linestyle='dashed', alpha=0.6)
        ax.axvline(self.max_Ebound, color='red', linestyle='dashed', alpha=0.6)


    def save(self, type_target, type_shifts):
        # save figs in images/New(Old) dir
        plt.subplots_adjust(hspace=0.3, wspace=0.4, left=0.07, right=0.98)
        if self.file_set == 'old':
            file_set = 'Old'
        else:
            file_set = 'New'

        dir_plt = os.path.join("images", file_set)
        if not os.path.isdir(dir_plt):
            os.mkdir(dir_plt)

        path_name = os.path.join(dir_plt, type_target + '_' + type_shifts + "_" + self.file_set + ".pdf")
        plt.savefig(path_name)
        print(f"Saved {path_name}")
