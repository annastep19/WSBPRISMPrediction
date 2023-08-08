# Wrong sign background PRISM prediction

## Code description 

Some notes:

- "Data" means Monte-Carlo simulation that is used as an input or output of code: (10.220.18.41)
- "$\leftarrow$" means that the functions from the script on the right are used in the left script 

### 1. Simplest comparison

To compare differences of nominal and shifted $'\nu_{\mu}'$ ND fluxes in FHC (neutrino mode) and RHC (antineutrino mode).

**Code:**

- *form_file.py* -- to extract and join unoscillated numu flux hists from different input files in one output file for each mode

**Data:**

- input files: 
  - /home/annast/project/neutrino/, 
  - /home/annast/antineutrino/
- output files: /home/annast/project/uncert/

Note: there are results for a few uncertainties: Decay Pipe Radius, Horn Current, Horn Water Layer Thickness, Proton Beam Radius. For a whole list of uncertainties see Pierce's directories.

### 2. One dimensional plots

**Code:**

- one_dim_ratios.py $\leftarrow$ one_dim_utils.py -- to launch ratio calculations at a particular position and create plots.
 
**Results:**
