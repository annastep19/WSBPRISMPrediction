import sys
sys.path.insert(0, ".")
from flux_fitter import *
from ErrorPlots import *


# oscillation probability
dcp = 0
s23 = 0.53
dm32 = 2.46e-3
osc_hyp = oscProb("numu", "numu", s23 = s23, dm32 = dm32, dcp = dcp)

# main class
fitter = flux_fitter(oscParam = osc_hyp,
                     file_set = '300_285',
                     useHC = True,
                     Erebin = 10,
                     OArebin = 10,
                     other_loaded = True, 
                     ppfx_loaded = True, 
                     PpfxUniv = 100)

# fit range
energies = [0.4, 3.865]
fitter.set_fit_region(energies)
weight = [0.8, 0]
fitter.set_OOR(weight)

# extract a target (FD flux)
FD_nom = fitter.FD_nom

# set a reg parameter for FHC FD
reg_FHC = 4e-9 

# change the target (FD flux)
fitter.add_new_FD()
FD_RHC_nom = fitter.FD_RHC_nom

# set a reg parameter for RHC FD
reg_RHC = 4e-9 

# plot uncertainies for ND PRISM and FD fluxes
plots = ErrorPlots(fitter)

# FHC: other uncertainties 
plots.shifted_plots('FHC', reg_FHC, 'other', Nreb=10, 
                     ylim_F=5e-15, ylim_R=[0.04, 0.04, 0.04])
# FHC: ppfx uncertainties 
plots.shifted_plots('FHC', reg_FHC, 'ppfx', ylim_F=5e-15, ylim_R=[0.1, 0.1, 0.1])
# RHC: other
plots.shifted_plots('RHC', reg_RHC, 'other', Nreb=10,
                     ylim_F=4e-16, ylim_R=[0.04, 0.04, 0.04])
# RHC: ppfx
plots.shifted_plots('RHC', reg_RHC, 'ppfx', ylim_F=4e-16, ylim_R=[0.1, 0.1, 0.1])
