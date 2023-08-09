# Wrong sign background PRISM prediction

Code of Anna Stepanova for DUNE-PRISM group. Section 2.1 and the directory of "linearComb/" are based on Daniel Douglas' code: https://github.com/DanielMDouglas/prism_fitting 

> Some notes:
> 
> - *Data* means Monte-Carlo simulation that is used as inputs or outputs and temporarily located in 10.220.18.41
> - *300* in names of python files means that the main horn current equals to 300 kA, *285* is for an additional horn current. There are some other values (290 kA, 293 kA, 296 kA) of the additional horn current in: /home/annast/WSBPRISMPrediction/neutrino/OtherHorns/

## 1. Comparison of muon neutrino fluxes in FHC and RHC modes in the near detector

To compare differences of nominal and shifted $\nu_{\mu}$ ND fluxes in FHC (neutrino mode) and RHC (antineutrino mode).

**Preparing root-file:**

To extract and join unoscillated numu flux hists from different input files in one output file for each mode:

```
- input files: /home/annast/WSBPRISMPrediction/neutrino/, 
               /home/annast/WSBPRISMPrediction/antineutrino/

- run script: python uncert/form_file.py

- output files: will be created in uncert/
```
The copy of outputs is in /home/annast/WSBPRISMPrediction/uncert/


> Note: there are results for a few uncertainties: Decay Pipe Radius, Horn Current, Horn Water Layer Thickness, Proton Beam Radius. For a whole list of uncertainties see Pierce's directories.

### 1.1 One dimensional plots
To make one dimensional ratio plots of numu fluxes in FHC and RHC modes for each focusing uncertainty at a particular position 

```
python uncert/one_dim_ratios.py 

NB: it uses uncert/one_dim_utils.py
```

See figures in **Results**

### 1.2 Two dimensional plots
To create 2D ratios of ND off-axis fluxes (shifted/nominal): muon neutrino fluxes in FHC and RHC modes

```
python uncert/twoDimRatios.py
```

See figures in **Results**

## 2. The DUNE-PRISM method for muon neutrino fluxes

**Preparing root-file:**

To produce a mode file of new (old) nominal and shifted fluxes

```
- input files:
  - old (Den's data file): 
    - /home/annast/WSBPRISMPrediction/all_HC.root
  - new (Pierce's data files): 
    - /home/annast/WSBPRISMPrediction/neutrino/ 
    - /home/annast/WSBPRISMPrediction/antineutrino/

- utils: FormFile.py, BaseCombine.py 
- run scripts: Init_range_300_285.py, 
               Init_range_old.py
- output files: will be created in outputs/
```
The copy of outputs is in:
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

> Note: there are no new ppfx fluxes. They will be converted from old ppfx fluxes directly. Look further.
  
**Making a linear combination**

```
cd linearComb/
```

- `fluxes.py` + `utils.py`:
  - to determine data files
  - to point syst shifts
  - to arrange fluxes in dicts (to set root-file and a single name of hist)
  - to set energy and off-axis ranges
- `flux_fitter.py` + `fluxes.py`, `utils.py`, `oscProbs.py`:
  - to load fluxes and set other variables
  > Note: load_FD_ppfx_shifts()/load_ND_ppfx_shifts(): 
    to produce new ppfx fluxes old ppfx fluxes are used for now
  - to change fit and OA range, 
  - to add a FD RHC flux as a new target
  - to calculate coefficients of linear combination
- `plots.py`:
  - to plot DUNE-PRISM linear combination, a target flux and LC coefficients
- `ErrorPlots.py`:
  - to plot ratios of nominal and shifted ND-PRISM and FD fluxes in FHC and RHC modes for old/new data files


**Run scripts**

To plot DUNE-PRISM linear combination flux and FD flux that is a target (FHC/RHC) and coefficients of them for:
- new data:

```
cd linearComb/

python examples/nom_coeff_300_285.py

NB: it uses plots.py
```

- old data:
```
cd linearComb/

python examples/nom_coeff_old.py

NB: it uses plots.py
```

To plot ratios of nominal and shifted fluxes for DUNE-PRISM LC off-axis fluxes and FD fluxes:
- new data: FHC/RHC, other/ppfx

```
cd linearComb/

python examples/shifts_300_285.py

NB: it uses ErrorPlots.py
```

- old data: FHC/RHC, other/ppfx
```
cd linearComb/

python examples/shifts_old.py

NB: it uses ErrorPlots.py
```

See figures in **Results**

## Results:

## 1. Comparison of muon neutrino fluxes in FHC and RHC modes in the near detector

### 1.1 One dimensional plots

New data:
- Horn Current: on-axis position 

![a](/imgs/jpg/LAr_center_Horn_current_OnAxis_0_m_page-0001.jpg)
![b](/imgs/jpg/LAr_center_Horn_current_OnAxis_0_m_page-0002.jpg)

### 1.2 Two dimensional plots

New data:

- Horn Current + 1 sigma

![c](/imgs/jpg/LAr_center_Horn_Current_pos_page-0001.jpg)

- Horn Current - 1 sigma

![d](/imgs/jpg/LAr_center_Horn_Current_neg_page-0001.jpg)

- Decay Pipe Radius + 1 sigma

![r](/imgs/jpg/LAr_center_Decay_Pipe_Radius_pos_page-0001.jpg)

- Decay Pipe Radius - 1 sigma

![s](/imgs/jpg/LAr_center_Decay_Pipe_Radius_neg_page-0001.jpg)

- Horn Current Water Layer Thickness + 1 sigma

![t](/imgs/jpg/LAr_center_Horn_Water_Layer_Thickness_pos_page-0001.jpg)

- Horn Current Water Layer Thickness - 1 sigma

![x](/imgs/jpg/LAr_center_Horn_Water_Layer_Thickness_neg_page-0001.jpg)

- Proton Beam Radius + 1 sigma

![y](/imgs/jpg/LAr_center_Proton_Beam_Radius_pos_page-0001.jpg)

- Proton Beam Radius - 1 sigma

![z](/imgs/jpg/LAr_center_Proton_Beam_Radius_neg_page-0001.jpg)

## 2. The DUNE-PRISM method for muon neutrino fluxes

New data:

- FHC

![e](/imgs/jpg/FHC_nom_coeff_300_285_page-0001.jpg)

- RHC

![f](/imgs/jpg/RHC_nom_coeff_300_285_page-0001.jpg)

Old data:

- FHC

![g](/imgs/jpg/FHC_nom_coeff_page-0001.jpg)

- RHC

![h](/imgs/jpg/RHC_nom_coeff_page-0001.jpg)

New data:
- FHC: other

![i](/imgs/jpg/FHC_other_300_285_page-0001.jpg)

- FHC: ppfx

![j](/imgs/jpg/FHC_ppfx_300_285_page-0001.jpg)

- RHC: other

![k](/imgs/jpg/RHC_other_300_285_page-0001.jpg)

- RHC: ppfx

![l](/imgs/jpg/RHC_ppfx_300_285_page-0001.jpg)

Old data:
- FHC: other

![m](/imgs/jpg/FHC_other_old_page-0001.jpg)

- FHC: ppfx

![o](/imgs/jpg/FHC_ppfx_old_page-0001.jpg)

- RHC: other

![p](/imgs/jpg/RHC_other_old_page-0001.jpg)

- RHC: ppfx

![q](/imgs/jpg/RHC_ppfx_old_page-0001.jpg)
