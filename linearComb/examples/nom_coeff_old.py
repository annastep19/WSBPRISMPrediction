import sys
sys.path.insert(0, ".")
from flux_fitter import *
from plots import plot_nom_fluxes_coeff


# oscillation probability
dcp = 0
s23 = 0.53
dm32 = 2.46e-3
osc_hyp = oscProb("numu", "numu", s23 = s23, dm32 = dm32, dcp = dcp)

# main class
fitter = flux_fitter(oscParam = osc_hyp,
                     file_set = 'old',
                     useHC = True,
                     Erebin = 5)

# fit range
energies = [0.4, 3.865]
fitter.set_fit_region(energies)
weight = [0.8, 0]
fitter.set_OOR(weight)

# extract a target (FD flux)
FD_nom = fitter.FD_nom

# set reg parameters for FHC FD
reg_FHC = 5e-9 

plot_nom_fluxes_coeff(reg_FHC, fitter, type_target='FHC', woHC=True, reg_wo=reg_FHC, ratio=False)

# change the target (FD flux)
fitter.add_new_FD()
FD_RHC_nom = fitter.FD_RHC_nom

# set reg parameters for RHC FD
reg_RHC = 5e-9 

plot_nom_fluxes_coeff(reg_RHC, fitter, type_target='RHC', woHC=True, reg_wo=reg_RHC, ratio=False)
