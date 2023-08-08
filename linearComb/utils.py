import numpy as np
from ROOT import *


def root_to_array(TH, binEdges = [], method = "average"):
    shape = [TH.GetNbinsX(),
             TH.GetNbinsY()]
    con = np.ndarray(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
                con[i,j] = TH.GetBinContent(i+1, j+1)
    con = con.squeeze()

    if list(binEdges):
        oldBins = list(root_to_axes(TH))
        if method == "average":
            for axis, theseBinEdges in enumerate(binEdges):
                con = average_by_bin_edge(con, oldBins[axis], theseBinEdges, axis = axis)
        elif method == "interpolate":
            for axis, theseBinEdges in enumerate(binEdges):
                theseBinCenters = 0.5*(theseBinEdges[:-1] + theseBinEdges[1:])
                con = np.interp(theseBinCenters, oldBins[axis], con)
    return con

def root_to_axes(TH, where = 'mid'):
    axes = [TH.GetXaxis(),
            TH.GetYaxis()]
    shape = [TH.GetNbinsX(),
             TH.GetNbinsY()]
    if where == 'mid':
        xBins = np.array([axes[0].GetBinCenter(i+1) for i in range(shape[0])])
        yBins = np.array([axes[1].GetBinCenter(i+1) for i in range(shape[1])])
    elif where == 'pre':
        xBins = np.array([axes[0].GetBinLowEdge(i+1) for i in range(shape[0])])
        yBins = np.array([axes[1].GetBinLowEdge(i+1) for i in range(shape[1])])
    elif where == 'post':
        xBins = np.array([axes[0].GetBinUpEdge(i+1) for i in range(shape[0])])
        yBins = np.array([axes[1].GetBinUpEdge(i+1) for i in range(shape[1])])
    else:
        raise KeyError("options are 'mid', 'pre', and 'post'")
    return (xBins, yBins)


def rebin(oldHist, rebinF, axis = 0):
    oldShape = oldHist.shape
    newShape = oldShape[:axis] + (oldShape[axis]//rebinF, rebinF) + oldShape[axis+1:]
    newHist = np.sum(oldHist.reshape(newShape), axis = axis + 1)
    return newHist

def rebin_by_bin_edge(oldHist, oldBinCenters, newBinEdges, axis = 0, side = 'left'):
    # WARNING: Only works for axis = 0 or 1 for now!
    oldShape = oldHist.shape
    newShape = oldShape[:axis] + tuple((newBinEdges.size-1,)) + oldShape[axis+1:]
    newHist = np.ndarray(newShape)
    if axis == 0:
        for i, (leftEdge, rightEdge) in enumerate(zip(newBinEdges[:-1], newBinEdges[1:])):
            if side == 'right':
                newHist[i] = np.sum(oldHist[np.logical_and(leftEdge < oldBinCenters,
                                                           oldBinCenters <= rightEdge)],
                                    axis = 0)
            else:
                newHist[i] = np.sum(oldHist[np.logical_and(leftEdge <= oldBinCenters,
                                                           oldBinCenters < rightEdge)],
                                    axis = 0)    
        return newHist
    elif axis == 1:
        for i in range(newHist.shape[0]):
            newHist[i] = rebin_by_bin_edge(oldHist[i], oldBinCenters, newBinEdges)
        return newHist


def average(oldHist, rebinF, **kwargs):
    return rebin(oldHist, rebinF, **kwargs)/float(rebinF)

def average_by_bin_edge(oldHist, oldBinCenters, newBinEdges, axis = 0, side = 'left'):
    rebinned = rebin_by_bin_edge(oldHist, oldBinCenters, newBinEdges, axis = axis)
    for i, (leftEdge, rightEdge) in enumerate(zip(newBinEdges[:-1], newBinEdges[1:])):
        if side == 'right':
            nInside = np.sum(np.logical_and(leftEdge < oldBinCenters,
                                            oldBinCenters <= rightEdge),
                             dtype = float)
        else:
            nInside = np.sum(np.logical_and(leftEdge <= oldBinCenters,
                                            oldBinCenters < rightEdge),
                             dtype = float)

        if axis == 0:
            rebinned[i] /= nInside
        elif axis == 1:
            rebinned[:, i] /= nInside
    return rebinned
