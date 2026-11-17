# Introduction  

The code file implementing the functionality is mu2e_v2.py, also symbolically linked as Mu2eNRET.py for compatability with the MuonConverter Repository.

This  code is intended to be a python equivalent of the Mathematica notebook ../mathematica/mu2e_v2.nb
The function names match between the Mathematica and Python code.

The elements data base can be found in elements.yaml in the same directory.

One-body density matrices for relevant  isotopes can be found in a companion repository
[github:Berkeley-Electroweak-Physics/Elastic](https://github.com/Berkeley-Electroweak-Physics/Elastic) .  You should clone this repository and set the environment variable MU2E_ELASTIC to it's full path.
If you were added to the access list for the Mu2E scripts then you should be on the access list for the Elastic directory.   If not, just ask.
```
export MU2E_ELASTIC=<clonepath>/Elastic
```

# Requirements
Mu2e requires several modules to be installed.  The file
requirements.txt lists the modules and minimum versions and
can be used with pip3 to make sure they are installed properly.
```
pip3 install -r requirements.txt 
```

# Running
Your input setup should be in a <mycase>.yaml file.

```
python3 mu2e.py [args]
python3 mu2e.py -help   # generates help message
```

A standard run will consume a yaml file specifying the required
data for the run.   "example.yaml" in this directory is a heavily commented template for 63Cu.  
```
python3 mu2e.py example.yaml  # run file example.yaml
```

mu2e also has an option to produce a Mathematica script to run the Mathematica version of the code.
```
python3 mu2e.py -wl example.yaml
```
This run will additionally produce example.wl (wl is a standard suffix for Mathematica files).    The beginning of the file will
explain how to run it.


The examples subdirectory has additional isotope specific examples.

Plots will be written to a directory who's name is the name of the element being processed.
