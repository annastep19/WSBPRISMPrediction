# Wrong sign background PRISM prediction

Code of Anna Stepanova for DUNE-PRISM group. Section 2.1 and the directory of "linearComb/" are based on Daniel Douglas' code: https://github.com/DanielMDouglas/prism_fitting 

> Some notes:
> 
> - *Data* means Monte-Carlo simulation that is used as inputs or outputs and located in 10.220.18.41
> - $\leftarrow$ means that functions from a script on the right are used in a left script 
> - *300* in names of python files means that the main horn current equals to 300 kA, *285* is for an additional horn current. There are some other values (290 kA, 293 kA, 296 kA) of the additional horn current in: /home/annast/WSBPRISMPrediction/neutrino/OtherHorns/

## 1. Comparison of muon neutrino fluxes in FHC and RHC modes in the near detector

To compare differences of nominal and shifted $\nu_{\mu}$ ND fluxes in FHC (neutrino mode) and RHC (antineutrino mode).

**Code:**

To extract and join unoscillated numu flux hists from different input files in one output file for each mode:

```
- input files: /home/annast/WSBPRISMPrediction/neutrino/, /home/annast/WSBPRISMPrediction/antineutrino/

- python script: `uncert/form_file.py`

- output files: will be created in uncert/.\ The copy is in /home/annast/WSBPRISMPrediction/uncert/
```

> Note: there are results for a few uncertainties: Decay Pipe Radius, Horn Current, Horn Water Layer Thickness, Proton Beam Radius. For a whole list of uncertainties see Pierce's directories.

### 1.1 One dimensional plots

**Code:**

- `one_dim_ratios.py` $\leftarrow$ `one_dim_utils.py` - to launch ratio calculations at a particular position and create plots
 

### 1.2 Two dimensional plots

**Code:**

- `twoDimRatios.py` - to create 2D ratios of ND off-axis fluxes


## 2. Modifications of Den's code

Data:

- input:
  - old data = Den's data file: 
    - all_HC.root
  - new data = Pierce's data files: 
    - /home/annast/WSBPRISMPrediction/neutrino/ 
    - /home/annast/WSBPRISMPrediction/antineutrino/

- output:
  - old data: 
    - /home/annast/WSBPRISMPrediction/outputs/neutrino_range_old.root
    - /home/annast/WSBPRISMPrediction/outputs/antineutrino_range_old.root
   
    ![1](/imgs/1.png)
    ![2](/imgs/2.png)

    ![3](/imgs/3.png)
    ![4](/imgs/4.png)

  - new data:
    - /home/annast/WSBPRISMPrediction/outputs/neutrino_range_300_285.root
    - /home/annast/WSBPRISMPrediction/outputs/antineutrino_range_300_285.root

    ![5](/imgs/5.png)
    ![6](/imgs/6.png)
  
  > Note: there are no new ppfx fluxes. They will be converted from old ppfx fluxes directly. See part 2.1


**Code:**

- `Init\_range\_old.py` $\leftarrow$ `FormFile.py, BaseCombine.py` - to produce a mode file of old fluxes
- `Init\_ragne\_300\_285.py` $\leftarrow$ `FormFile.py, BaseCombine.py` - the same for new fluxes


### 2.1 Making a linear combination

**Code:**

- `fluxes.py` $\leftarrow$ `utils.py`:
  - to determine data files
  - to point syst shifts
  - to arrange fluxes in dicts (to set root-file and a single name of hist)
  - to set energy and off-axis ranges

- `flux_fitter.py` $\leftarrow$ `fluxes.py, utils.py, plots.py`: 

  - to load fluxes and set other variables
  
  > Note: load_FD_ppfx_shifts()/load_ND_ppfx_shifts(): to produce new ppfx fluxes old ppfx fluxes are used for now

  - to change fit and OA range, 
  - to add a FD RHC flux as a new target
  - to calculate coefficients of linear combination
  
- `ErrorPlots.py`


**Results:**

- to plot DUNE-PRISM linear combination flux and FD flux that is a target,  coefficients of them:
  - `examples/nom_coeff_300_285.py` $\leftarrow$ `plots.py, flux_fitter.py` - new data: 
    - FHC
    - RHC
  - `examples/nom_coeff_old.py` $\leftarrow$ `plots.py, flux_fitter.py` - old data:
    - FHC
    - RHC
- to plot ratios of nominal and shifted fluxes: for DUNE-PRISM LC off-axis fluxes and FD fluxes
  - `examples/shifts_300_285.py` $\leftarrow$ `ErrorPlots.py, flux_fitter.py` - new data:
    - FHC:
       - focusing 
       - ppfx
    - RHC
       - focusing
       - ppfx
  - `examples/shifts_old.py` $\leftarrow$ `ErrorPlots.py, flux_fitter.py` - old data:
    - FHC:
       - focusing 
       - ppfx
    - RHC
       - focusing 
       - ppfx

## Results:

### 1.1 One dimensional plots

![a](/imgs/jpg/LAr_center_Horn_current_OnAxis_0_m_page-0001.jpg)
![b](/imgs/jpg/LAr_center_Horn_current_OnAxis_0_m_page-0002.jpg)

### 1.2 Two dimensional plots

![c](/imgs/jpg/LAr_center_Horn_Current_pos_page-0001.jpg)
![d](/imgs/jpg/LAr_center_Horn_Current_neg_page-0001.jpg)

### 

![e](/imgs/jpg/FHC_nom_coeff_300_285_page-0001.jpg)
![f](/imgs/jpg/RHC_nom_coeff_300_285_page-0001.jpg)

![g](/imgs/jpg/FHC_nom_coeff_page-0001.jpg)
![h](/imgs/jpg/RHC_nom_coeff_page-0001.jpg)

![i](/imgs/jpg/FHC_other_300_285_page-0001.jpg)
![j](/imgs/jpg/FHC_ppfx_300_285_page-0001.jpg)

![k](/imgs/jpg/RHC_other_300_285_page-0001.jpg)
![l](/imgs/jpg/RHC_ppfx_300_285_page-0001.jpg)

![m](/imgs/jpg/FHC_other_old_page-0001.jpg)
![o](/imgs/jpg/FHC_ppfx_old_page-0001.jpg)

![p](/imgs/jpg/RHC_other_old_page-0001.jpg)
![q](/imgs/jpg/RHC_ppfx_old_page-0001.jpg)

