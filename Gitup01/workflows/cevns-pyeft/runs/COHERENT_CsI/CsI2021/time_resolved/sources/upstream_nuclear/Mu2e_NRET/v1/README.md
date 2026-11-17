# Mu2E
Scripts and data files for nuclear muon to electron conversion analysis.

**Note**: this README file is best viewed in a markdown viewer that supports embedded latex equations.   One such viewer is PanWriter.

There are both Mathematica and Python scripts.
The main advantage of the Mathematica script is that symbolic expressions can be generated for matrix elements.

# Mathematica

The file mu2e_eft.nb is the top level file.   It will load mu2elib.m for function definitions.  mu2elib.m should remain in the same directory as mu2e_eft.nb so it can be found.

This mathematica notebook also requires the Elastic directory of repository 
```
git@github.com:Berkeley-Electroweak-Physics/StructureResults.git.
```
Clone the repository and set an environment variable so the Mathematica code can find it.
```bash
export MU2E_STRUCTURERESULTS=<path-to-structure-results>
```
Running this notebook is an interactive process.   Use the "Evaluate Notebook" command.   Prompts will ask for the element and isotope choice.   The isotope choice can be an average over abundances or a specific isotope.   Then an interaction is requested.

# Python  
The python script is called "mu2e.py".   Required data about elements and isotopes can be found in a file elements.yaml in the same directory.    

# Requirements  
Like the Mathematica script mu2e.py reads one-body density matrices from a clone of 
```
git@github.com:Berkeley-Electroweak-Physics/StructureResults.git.
```
Clone the repository and set an environment variable so the Mathematica code can find it.
```bash
export MU2E_STRUCTURERESULTS=<path-to-structure-results>
```

You will also need to make sure you have some required python packages installed.
```bash
pip3 install argparse         # command line parsing
pip3 install pathlib          # File system api
pip3 install pprint           # Pretty printer for data
pip3 install multipledispatch # function overloading
pip3 install pyyaml           # python data files.  
                              # Used for isotope data
pip3 install py3nj            # implements 3J, 6J, 9J symbols
pip3 install numpy            # arrays, matrices, tensors, ...
pip3 install scipy            # A variety of special functions
                              #  hypergeometric, integration, ...
pip3 install matplotlib       # Powerful plotting package.
```

# Running  
Unlike the Mathematica notebook, mu2e.py uses a yaml file for input data.   We include an example file called example.yaml .  This file has plenty of comments explaining the fields to set.

Command line options can be found using
```
python3 mu2e.py -h
```
A typical run will look like
```
python3 mu2e.py example.py
```
Plots will be placed in a directory named after the element being analysed.   Plots will be saved in a pdf format.   They are constructed with the matplotlib package.
