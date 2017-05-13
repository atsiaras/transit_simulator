# TransitSimulator

Interactive transit simulator.


Includes the package:

* [PyLightcurve](https://github.com/ucl-exoplanets/pylightcurve)

which also includes the following packages:

* [oec](https://github.com/OpenExoplanetCatalogue/open_exoplanet_catalogue), [Rein (2012)](https://arxiv.org/abs/1211.7121)
* [exodata](https://github.com/ryanvarley/ExoData), [Varley (2016)](http://www.sciencedirect.com/science/article/pii/S0010465516301254)
* [emcee](https://github.com/dfm/emcee), [Foreman-Mackey et al. (2013)](http://iopscience.iop.org/article/10.1086/670067)


# Installation

This module depends on

* matplotlib
* numpy
* astropy
* quantities

### From terminal
Download, unzip and `cd` in this repo. Then type `python setup.py install`.

### Quick way
Double-click on the appropriate installer (osx, linux or windows).
The package will be installed as every python package and a command file will 
be created in your Desktop.

# Usage

### From terminal
	>>> import transit_simulator
	
	>>> transit_simulator.run_app()

### Quick way
Double-click on the command file created in your Desktop.


# Updates from version 1.0

* Use the updated version of the PyLightcurve package (1.1). Important new feature: tri-linear interpolation for the 
calculation of the limb darkening coefficients on the tables provided by Claret and Bloeman 2012 (only the 4 non-linear 
coefficients (Claret 2002) are currently available).
