# Introduction
This code implements a nonrelativistic effective theory for muon to electron conversion with the muon starting in the lowest atomic orbital.   The conversion is described by an interaction with the nucleus which has been factored in to a target dependent nuclear matrix element and an effective interaction with a nucleon characterized by LECs.   This earlier version does not include tensor interactions or the lower components of the muon Dirac spinor.   See version 2 for those features.

This  code is intended to be a python equivalent for the Mathematica notebook in ../mathematica.
The function names match between the Mathematica and Python code.

The elements data base can be found in elements.yaml in the same directory.

One-body density matrices for relevant  isotopes can be found in a companion repository
[github:Berkeley-Electroweak-Physics/Elastic](https://github.com/Berkeley-Electroweak-Physics/Elastic) .  You should clone this repository and set the environment variable MU2E_ELASTIC to it's full path.
If you were added to the access list for the Mu2E scripts then you should be on the access list for the Elastic directory.   If not, just ask.
```
export MU2E_ELASTIC=<clonepath>/Elastic
```

# Running
Your input setup should be in a <mycase>.yaml file.

```
python3 mu2e_v1.py [args]
python3 mu2e_v1.py -help   # generates help message
```

See example.yaml for an example with notes.   The examples directory has addition isotope specific examples.

Plots will be written to a directory who's name is the name of the element being processed.

# Requirements

Mu2e requires several modules to be installed.  The file
requirements.txt lists the modules and minimum versions and
can be used with pip3 to make sure they are installed properly.
```
pip3 install -r requirements.txt 
```
The explicit list is
```
pip3 install multipledispatch   # function overloading
pip3 install pyyaml             # python data files.  
                                # Used for isotope data
pip3 install py3nj              # implements 3J, 6J, 9J symbols
pip3 install numpy              # efficient arrays and operations
pip3 install scipy              # A variety of special functions
                                #  hypergeometric, integration
```
# Tests 
The original version of the script was a Mathematica one.   We have created various test setups in the subdirectory called test that will crosscheck the decayrate.
