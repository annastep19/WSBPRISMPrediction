import numpy as np

from Prob3 import BargerPropagator

# define the path length
LengthParam = 0
DipAngle_degrees = 5.8
LengthParam = np.cos(np.radians(90.0 + DipAngle_degrees))

# neutrino types are:
#     0: data_type (don't use)
#     1: nue_type
#     2: numu_type
#     3: nutau_type
#     4: sterile_type
#     5: unknown_type
ToType = 2
FromType = 2

# initialize the propagator
bp = BargerPropagator()
bp.DefinePath(LengthParam, 0)

Espace = np.linspace(0, 10, 1000)
Pspace = []
for E in Espace:
    # parameters to SetMNS are:
    # s_12, s_13, s_23,
    # dm_21, dm_atm, d_cp,
    # E, kSquared, flavor
    bp.SetMNS(0.846, 0.093, 0.92,
              7.53e-5, 2.44e-3, 0.0,
              E, True, FromType)
    bp.propagate(ToType)
    prob = bp.GetProb(FromType, ToType)
    Pspace.append(prob)

import matplotlib.pyplot as plt
plt.plot(Espace, Pspace)
plt.ylim(0, 1)
plt.xlabel(r'$E_\nu$ (GeV)')
plt.ylabel(r'$P (\nu_\mu \rightarrow \nu_\mu)$')
plt.show()
