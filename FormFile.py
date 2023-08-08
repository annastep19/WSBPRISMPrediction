from ROOT import TFile, TH2D, TH1D, TList
import numpy as np


class FormFile:
    """take hist and *change* them
 
    Methods:    
        -- __init__(): define output file
        -- add(): write hist in output file (is used in Init_range...py)
           _cut_ranges_()(and normalize: DivWidthGeV), _scale()_ : change hist if necessary
        -- HC_other_new(): create other HC flux for new set
           _read()_: read hist
        -- HC_other_old(): create other HC flux for old set
           _read()_: read hist
        -- close(): close output file
    """    
    def __init__(self, output_file, cut=False, scale=0, add_bin=0, **kwargs):
        self.output_file = TFile(output_file, "update")
        
        self.cut = cut
        if self.cut:
            self.ERange = kwargs["ERange"]
            self.LocRange = kwargs["LocRange"]
            self.DivWidthGeV = kwargs.get("DivWidthGeV", False)

        self.scale = scale
        self.add_bin = add_bin


    def add(self, detector_name, output_hist_name, output_hist_type, 
                  input_hist: tuple):
        """read hist,
           *cut/divide by width and scale*,
           write hist in output file
        Args:
            detector_name (str): directory in output file
            output_hist_name (str): hist name in output file
            output_hist_type (str): hist type for __cut_ranges__() and __scale__()
            input_hist (tuple): input file path and initial hist name
        """
        assert (output_hist_type != "1D" or output_hist_type != "2D"), f"{output_hist_type}" 
        assert isinstance(input_hist, tuple), f"3 arg is tuple"

        input_file_path = input_hist[0]
        input_hist_name = input_hist[1]
        input_file = TFile(input_file_path, "read")
        hist = input_file.Get(input_hist_name)

        if self.cut:
            title = input_file.GetName().split("/")[-1].split(".root")[0]
            hist = self._cut_ranges_(hist, output_hist_type, title) 
        if self.scale:
            hist = self._scale_(hist, output_hist_type)

        # write in output_file
        if not self.output_file.GetDirectory(detector_name + ";1"):
            self.output_file.mkdir(detector_name)

        self.output_file.cd(detector_name + ";1")
        hist.Write(output_hist_name, option=2)
        input_file.Close()   
        

    def _cut_ranges_(self, hist, hist_type, title):
        """cut, *divide by width*
        Args:
            hist: initial hist
            hist_type (str): 1D/2D 
            title: title of cutted hist
        Returns:
            cut_hist: cutted, *divided by width in GeV* hist
        """
        TAX = hist.GetXaxis()
        TAY = hist.GetYaxis()

        xMinBin = TAX.FindBin(self.ERange[0])
        xMaxBin = TAX.FindBin(self.ERange[1])
        xBins = xMaxBin - xMinBin

        if hist_type == "1D":
            shape = [xBins]
            flux = np.ndarray(shape)
            err = np.ndarray(shape)
            if self.DivWidthGeV:
                width = np.ndarray(shape)
            energy = np.ndarray(shape[0])
            
            cut_hist = TH1D(title, title, 
                            shape[0], self.ERange[0], self.ERange[1])

            for i, xNum in enumerate(range(xMinBin, xMaxBin)):
                    energy[i] = TAX.GetBinCenter(xNum)
                    flux[i] = hist.GetBinContent(xNum)
                    if self.DivWidthGeV:
                        width[i] = hist.GetBinWidth(xNum)
                        flux[i] = flux[i]/width[i]
                        yNameAdd = " / GeV"
                    err[i] = hist.GetBinError(xNum)
                    cut_hist.Fill(energy[i], flux[i])
                    cut_hist.SetBinError(xNum, err[i])

            yLabel = TAY.GetTitle()
            if self.DivWidthGeV:
                cut_hist.GetYaxis().SetTitle(yLabel+yNameAdd)
            else:
                cut_hist.GetYaxis().SetTitle(yLabel)
        else:
            TAZ = hist.GetZaxis()

            yMinBin = TAY.FindBin(self.LocRange[0])
            yMaxBin = TAY.FindBin(self.LocRange[1])
            yBins = yMaxBin - yMinBin

            # !!! problem with bin !!!
            if self.add_bin == 1:
                yBins += 1 

            shape = [xBins, yBins]
            flux = np.ndarray(shape)
            err = np.ndarray(shape)
            if self.DivWidthGeV:
                width = np.ndarray(shape[0])
            energy = np.ndarray(shape[0])
            loc = np.ndarray(shape[1])
            
            cut_hist = TH2D(title, title, 
                            shape[0], self.ERange[0], self.ERange[1], 
                            shape[1], self.LocRange[0], self.LocRange[1])
            for j, yNum in enumerate(range(yMinBin, yMaxBin)):
                for i, xNum in enumerate(range(xMinBin, xMaxBin)):
                    energy[i] = TAX.GetBinCenter(xNum)
                    loc[j] = TAY.GetBinCenter(yNum)
                    flux[i,j] = hist.GetBinContent(xNum, yNum)
                    if self.DivWidthGeV:
                        width[i] = TAX.GetBinWidth(xNum)
                        flux[i, j] = flux[i, j]/width[i]
                        zNameAdd = " / GeV"
                    err[i,j] = hist.GetBinError(xNum, yNum)
                    cut_hist.Fill(energy[i], loc[j], flux[i,j])
            yLabel = TAY.GetTitle()
            zLabel = TAZ.GetTitle()
            cut_hist.GetYaxis().SetTitle(yLabel)

            if self.DivWidthGeV:
                cut_hist.GetZaxis().SetTitle(zLabel+zNameAdd)
            else:                
                cut_hist.GetZaxis().SetTitle(zLabel)

        xLabel = TAX.GetTitle()
        cut_hist.GetXaxis().SetTitle(xLabel)
        return cut_hist
           
    def _scale_(self, hist, hist_type):
        """ multiply by scalar from self.scale """
        hist.Scale(self.scale)
        if self.scale == 0.0001 and self.DivWidthGeV:
            if hist_type == "1D": 
                hist.GetYaxis().SetTitle("flux #nu_{#mu}s / cm^{2} / POT / GeV")
            else:
                hist.GetZaxis().SetTitle("Unosc #nu_{#mu}s / cm^{2} / POT / GeV")
        else:
            prev_title = hist.GetZaxis().GetTitle()
            if hist_type == "1D": 
                hist.GetYaxis().SetTitle(prev_title + "*" + str(self.scale))
            else:
                hist.GetZaxis().SetTitle(prev_title + "*" + str(self.scale))
        return hist


    def HC_other_new(self, detector_name, output_hist_name, input_hist_type, 
                           input_hists: tuple):
        """divide 1D shifted and nominal ND fluxes,
           multiply to nominal 1D HC flux
           write hist in output file

        Args:
           detector_name, output_hist_name (str): about returned hist
           input_hist_type: 1D
           input_hists (tuple): about shifted 1D ND hist, 
                                      nominal 1D ND hist,
                                      nominal 1D HC hist
        """

        input_file_path, input_hist_name = input_hists[0]
        old_norm_file_path, old_norm_hist_name = input_hists[1]
        new_norm_file_path, new_norm_hist_name = input_hists[2]

        input_file = TFile(input_file_path, "read")
        output_hist = self._read_(input_hist_type, input_file, input_hist_name)

        old_norm_file = TFile(old_norm_file_path, "read")
        old_norm_hist = self._read_(input_hist_type, old_norm_file, old_norm_hist_name)

        new_norm_file = TFile(new_norm_file_path, "read")
        new_norm_hist = self._read_(input_hist_type, new_norm_file, new_norm_hist_name)
        
        output_hist.Divide(old_norm_hist)
        output_hist.Multiply(new_norm_hist)

        # write in output_file
        if not self.output_file.GetDirectory(detector_name + ";1"):
            self.output_file.mkdir(detector_name)

        self.output_file.cd(detector_name + ";1") 
        output_hist.Write(output_hist_name, option=2)
        old_norm_file.Close()        
        new_norm_file.Close()
        input_file.Close()


    def HC_other_old(self, detector_name, output_hist_name,
                           input_hists: tuple):
        """divide 2D shifted and nominal ND fluxes,
           extract 1D ratio and multiply to nominal 1D HC flux
           write hist in output file

        Args:
           detector_name, output_hist_name (str): about returned hist
           input_hists (tuple): about shifted 2D ND hist, 
                                      nominal 2D ND hist,
                                      nominal 1D HC hist
        Func:
           _read_(): take hist and *change* it
        """
        input_file_path, input_hist_name = input_hists[0]
        old_norm_file_path, old_norm_hist_name = input_hists[1]
        new_norm_file_path, new_norm_hist_name = input_hists[2]

        input_file = TFile(input_file_path, "read")
        output_hist = self._read_("2D", input_file, input_hist_name)

        old_norm_file = TFile(old_norm_file_path, "read")
        old_norm_hist = self._read_("2D", old_norm_file, old_norm_hist_name)

        new_norm_file = TFile(new_norm_file_path, "read")
        new_norm_hist = self._read_("1D", new_norm_file, new_norm_hist_name)
        
        output_hist.Divide(old_norm_hist)

        # extract 1D from 2D ratio 
        TAX = output_hist.GetXaxis()
        shape = output_hist.GetNbinsX()
        energy = np.ndarray(shape)
        flux = np.ndarray(shape)
        err = np.ndarray(shape)

        hist_sh = TH1D("shifted HC", 'shifted HC', 
                        shape, self.ERange[0], self.ERange[1])

        for i in range(shape):
            energy[i] = TAX.GetBinCenter(i+1)
            flux[i] = output_hist.GetBinContent(i+1, 1)
            err[i] = output_hist.GetBinError(i+1)
            hist_sh.Fill(energy[i], flux[i])
            hist_sh.SetBinError(i+1, err[i])

        hist_sh.Multiply(new_norm_hist)
        xtit = new_norm_hist.GetYaxis().GetTitle()
        ytit = new_norm_hist.GetYaxis().GetTitle()
        hist_sh.GetXaxis().SetTitle(xtit)
        hist_sh.GetYaxis().SetTitle(ytit)

        # write in output_file
        if not self.output_file.GetDirectory(detector_name + ";1"):
            self.output_file.mkdir(detector_name)

        self.output_file.cd(detector_name + ";1") 
        hist_sh.Write(output_hist_name, option=2)
        old_norm_file.Close()        
        new_norm_file.Close()
        input_file.Close()

    def _read_(self, d_type, i_file, h_name):
            hist = i_file.Get(h_name)

            if self.cut:
                title = i_file.GetName().split("/")[-1].split(".root")[0]
                hist = self._cut_ranges_(hist, d_type, title) 
            if self.scale:
                hist = self._scale_(hist, d_type)
    
            return hist

    def close(self):
        self.output_file.Close()               
