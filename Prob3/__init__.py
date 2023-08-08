import ctypes
import os

dll_name = "libThreeProb.so"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
lib = ctypes.cdll.LoadLibrary(dllabspath)

class BargerPropagator(object):
    def __init__(self):
        lib.BargerPropagator_new.argtypes = []
        lib.BargerPropagator_new.restype = ctypes.c_void_p

        lib.BargerPropagator_propagate.argtypes = [ctypes.c_void_p,
                                                   ctypes.c_int]
        lib.BargerPropagator_propagate.restype = ctypes.c_void_p

        lib.BargerPropagator_propagateLinear.argtypes = [ctypes.c_void_p,
                                                         ctypes.c_int,
                                                         ctypes.c_double,
                                                         ctypes.c_double]
        lib.BargerPropagator_propagateLinear.restype = ctypes.c_void_p

        lib.BargerPropagator_GetVacuumProb.argtypes = [ctypes.c_void_p,
                                                       ctypes.c_int,
                                                       ctypes.c_int,
                                                       ctypes.c_double,
                                                       ctypes.c_double]
        lib.BargerPropagator_GetVacuumProb.restype = ctypes.c_double

        lib.BargerPropagator_DefinePath.argtypes = [ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_bool]
        lib.BargerPropagator_DefinePath.restype = ctypes.c_void_p

        lib.BargerPropagator_SetMNS.argtypes = [ctypes.c_void_p,
                                                ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                                ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                                ctypes.c_double, ctypes.c_bool, ctypes.c_int]
        lib.BargerPropagator_SetMNS.restype = ctypes.c_void_p

        lib.BargerPropagator_SetDensityConversion.argtypes = [ctypes.c_void_p,
                                                              ctypes.c_double]
        lib.BargerPropagator_SetDensityConversion.restype = ctypes.c_void_p

        lib.BargerPropagator_GetProb.argtypes = [ctypes.c_void_p,
                                                 ctypes.c_int, ctypes.c_int]
        lib.BargerPropagator_GetProb.restype = ctypes.c_double

        lib.BargerPropagator_GetPathLength.argtypes = [ctypes.c_void_p]
        lib.BargerPropagator_GetPathLength.restype = ctypes.c_double

        lib.BargerPropagator_SetPathLength.argtypes = [ctypes.c_void_p,
                                                       ctypes.c_double]
        lib.BargerPropagator_SetPathLength.restype = ctypes.c_void_p

        lib.BargerPropagator_SetEnergy.argtypes = [ctypes.c_void_p,
                                                   ctypes.c_double]
        lib.BargerPropagator_SetEnergy.restype = ctypes.c_void_p

        lib.BargerPropagator_SetMatterPathLength.argtypes = [ctypes.c_void_p]
        lib.BargerPropagator_SetMatterPathLength.restype = ctypes.c_void_p

        lib.BargerPropagator_SetAirPathLength.argtypes = [ctypes.c_void_p,
                                                          ctypes.c_double]
        lib.BargerPropagator_SetAirPathLength.restype = ctypes.c_void_p

        lib.BargerPropagator_UseMassEigenstates.argtypes = [ctypes.c_void_p,
                                                            ctypes.c_bool]
        lib.BargerPropagator_UseMassEigenstates.restype = ctypes.c_void_p

        lib.BargerPropagator_SetWarningSuppression.argtypes = [ctypes.c_void_p,
                                                               ctypes.c_bool]
        lib.BargerPropagator_SetWarningSuppression.restype = ctypes.c_void_p

        lib.BargerPropagator_SetOneMassScaleMode.argtypes = [ctypes.c_void_p,
                                                             ctypes.c_bool]
        lib.BargerPropagator_SetOneMassScaleMode.restype = ctypes.c_void_p

        self.obj = lib.BargerPropagator_new()

    def propagate(self, nuFlavor):
        lib.BargerPropagator_propagate(self.obj, nuFlavor)

    def propagateLinear(self, nuFlavor, pathLength, Density):
        return lib.BargerPropagator_propagate(self.obj, nuFlavor, pathLength, Density)

    def GetVacuumProb(self, Alpha, Beta, Energy, Path):
        return lib.BargerPropagator_GetVacuumProb(self.obj, Alpha, Beta, Energy, Path)

    def DefinePath(self, cz, ProdHeight, kSetProfile = True):
        lib.BargerPropagator_DefinePath(self.obj, cz, ProdHeight, kSetProfile)

    def SetMNS(self, x12, x13, x23,
               m21, mAtm, delta,
               Energy_, kSquared, kNuType):
        lib.BargerPropagator_SetMNS(self.obj, x12, x13, x23,
                                    m21, mAtm, delta,
                                    Energy_, kSquared, kNuType)

    def SetDensityConversion(self, x):
        return lib.BargerPropagator_SetDensityConversion(self.obj, x)

    def GetProb(self, nuIn, nuOut):
        return lib.BargerPropagator_GetProb(self.obj, nuIn, nuOut)

    def GetPathLength(self):
        return lib.BargerPropagator_GetPathLength(self.obj)
    
    def SetPathLength(self, x):
        return lib.BargerPropagator_SetPathLength(self.obj, x)

    def SetEnergy(self, x):
        return lib.BargerPropagator_SetEnergy(self.obj, x)

    def SetMatterPathLength(self):
        return lib.BargerPropagator_SetMatterPathLength(self.obj)

    def SetAirPathLength(self, x):
        return lib.BargerPropagator_SetAirPathLength(self.obj, x)

    def UseMassEigenstates(self, x):
        return lib.BargerPropagator_UseMassEigenstates(self.obj, x)

    def SetWarningSuppression(self, x):
        return lib.BargerPropagator_SetWarningSuppression(self.obj, x)

    def SetOneMassScaleMode(self, x):
        return lib.BargerPropagator_SetOneMassScaleMode(self.obj, x)
