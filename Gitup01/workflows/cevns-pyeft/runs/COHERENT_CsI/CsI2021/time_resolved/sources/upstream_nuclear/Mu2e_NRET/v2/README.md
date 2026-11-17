# Mu2e
The Mu2e repository contains Scripts and data files for nuclear muon to electron conversion analysis.  These scripts depend on an additional repository, [Elastic](git@github.com:Berkeley-Electroweak-Physics/Elastic.git), containing one-body density matrices for the nuclear targets of interest.  Density matrices were calculated with multiple interactions when possible as a measure of uncertainty. 

There are both Mathematica and Python scripts for the process.  Both require the same set of input data.
The script based python flow uses a Yaml data file to specify input data and options as a dictionary.
The script based Mathematica flow uses an "association" (the equivalent of a dictionary) to specify the
same data and options.

For Mathematica  a notebook mu2e.nb provides an interactive interface that prompts for the required input:
1) Target isotope choice  
2) Shell model interaction  
3) An optional harmonic oscillator length scale, with the default determined by the selected interaction  
4) A selection of no response function, analytic response function, or a plot of the response function. For response functions, one can select   
  - isoscalar: 1  
  - isovector: $\tau_)$  
  - proton: $\frac{1}{2}(1+\tau_3)$  
  - neutron:  $\frac{1}{2}(1-\tau_3)$  
5) For non-relativistic LECs (cs) specify a leptonic scale of 0.  For relativistic LECs (ds) specify a leptonic scale of the neutron mass.  (note that the specific value of the scale isn't important except that it must match code generating the LECs from higher level theories  
6) For the relativistic case you have the option of including the lower Dirac muon components in the calculation  
6) Specify the matching LECs
  - Non-relativistic:   The "cs" LECs  
  - Relativistic:  The "ds" LECs  
7) Finally, you have the option to override the default ordinary muon capture rate used in the branching ratio calculation 

Python example input is specified in the form of a *yaml* file describes a dictionary with entries corresponding the information above.  The code can also be imported and called directly with a dictionary, facilitating scanning of input LEC values.  

One advantage of the Mathematica script is that symbolic expressions can be generated for response functions.

# Mathematica

The file mathematica/mu2e.nb is the interactive notebook.   
It will load mu2elib.wl for function definitions.  mu2elib.wl should remain in the same directory as mu2e.nb so it can be found.

This mathematica notebook also requires the Elastic directory containing
ground state to ground state one-body density matrices.
Clone the repository in a directory parallel to the Mu2E clone.
```bash
git clone git@github.com:Berkeley-Electroweak-Physics/Elastic.git
```
and and set an environment variable so the Mathematica code can find it.
```bash
export MU2E_ELASTIC=<path-to-elastic-dir>
```
Running this notebook is an interactive process.   Use the "Evaluate Notebook" command.   Prompts will ask for the element and isotope choice.   The isotope choice can be an average over abundances or a specific isotope.   Then an interaction is requested.

# Python  
The python script is called "mu2e_v2.py".   Required data about elements and isotopes can be found in a file elements.yaml in the same directory.  

The README.md file in the python subdirectory gives more details on setup and running of the script.


