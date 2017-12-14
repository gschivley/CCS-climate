[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/gschivley/CCS-climate/master)

# Climate Benefits of Carbon Capture Depend on Timing and Methane Emission Uncertainty

## Setup
- Clone this repository.
- Make sure that you have anaconda installed.
- In a terminal/command prompt, navigate to the cloned folder
- Run `conda env -f environment.yml` to create an environment with the necessary packages
- Change your working anaconda environment with `conda activate ccs-timing` or `source activate ccs-timing` (or just `activate ccs-timing` on Windows)


This repository contains code that calculates the radiative forcing (RF) and cumulative radiative forcing (CRF) from the operation of new coal and natural gas power plants over a range of carbon capture and storage (CCS) and methane leakage scenarios. The code is split into two Jupyter notebooks:
- [Emissions](https://github.com/gschivley/CCS-climate/blob/master/Notebooks/Emissions.ipynb), which sets up emissions from each of the scenarios
- [Forcing Calculations](https://github.com/gschivley/CCS-climate/blob/master/Notebooks/Forcing%20Calculations.ipynb), which uses the emission distributions to calculate RF and CRF
