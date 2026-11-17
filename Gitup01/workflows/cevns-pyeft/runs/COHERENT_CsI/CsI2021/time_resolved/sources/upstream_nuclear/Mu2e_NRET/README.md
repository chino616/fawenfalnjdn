# Mu2e_NRET
Muon to electron conversion -  non-relativistic effective theory (NRET).

This repository contains two versions of the code in directories *v1* and *v2*.  In the article where this code is described these directories coorespond to **Mu2e_NRET_v1** and **Mu2e_NRET_v2**.   The *v1* version is the original code described in ${}^{[Mu2e]}$ and ${}^{[Mu2eFA]}$.  The *v2* version of the code is described in a more recent article connecting standard model effective theory (SMEFT) to the nucleus level NRET.

# Contents
This repository contains Python and Mathematica implementations of a nonrelativistic effective theory
(NRET) appropriate for analyzing nuclear experiments.   There are two versions.   The first version,
described in <sup>[Mu2e]</sup> and <sup>[Mu2eFA]</sup>, describes the conversion process begining with the
replacement of the 1s electron with a muon and the subsequent interaction with the nucleus.   The first version
was carried out to first order in the nucleon and muon velocities.   A second version, developed in support of
connecting to higher level theories was extended to include tensor operators, and relativisic corrections associated
with the lower components of the muon wavefunction.   

This repository depends on a collection of one-body density matrices for nuclear targets.    [The Elastic repository](https://github.com/Berkeley-Electroweak-Physics/Elastic) 
contains the required files.

Two additional repositories 
[MuonBridge](https://github.com/Berkeley-Electroweak-Physics/MuonBridge) 
and 
[MuonConverter](https://github.com/Berkeley-Electroweak-Physics/MuonConverter), 
found in this github organization,
implement reduction from Standard Model Effective Theories (SMEFT).    MuonBridge is an overview repository with scripts to
clone a set of consistant versions of the other required repositories.    MuonConverter implements the reduction from SMEFT LECs to
the Muon_NRET LECs.

Version 1 of Mu2e_NRET can be found in subdirectory **v1**.   See the README.md file there for more details.

Version 2 of Mu2e_NRET can be found in subdirectory **v2**.   See the README.md file there for more details.

# Citation

If you use this software in your work, please include these citations

```
@article{PhysRevLett.130.131901,
  title = {Nuclear-Level Effective Theory of $\ensuremath{\mu}\ensuremath{\rightarrow}e$ Conversion},
  author = {Rule, Evan and Haxton, W. C. and McElvain, Kenneth},
  journal = {Phys. Rev. Lett.},
  volume = {130},
  issue = {13},
  pages = {131901},
  numpages = {6},
  year = {2023},
  month = {Mar},
  publisher = {American Physical Society},
  doi = {10.1103/PhysRevLett.130.131901},
  url = {https://link.aps.org/doi/10.1103/PhysRevLett.130.131901}
}

@article{PhysRevC.107.035504,
  title = {Nuclear-level effective theory of $\ensuremath{\mu}\ensuremath{\rightarrow}e$ conversion: Formalism and applications},
  author = {Haxton, W. C. and Rule, Evan and McElvain, Ken and Ramsey-Musolf, Michael J.},
  journal = {Phys. Rev. C},
  volume = {107},
  issue = {3},
  pages = {035504},
  numpages = {43},
  year = {2023},
  month = {Mar},
  publisher = {American Physical Society},
  doi = {10.1103/PhysRevC.107.035504},
  url = {https://link.aps.org/doi/10.1103/PhysRevC.107.035504}
}
```

# References  

\[Mu2e\]: "Nuclear-Level Effective Theory of Muon -> Electron Conversion", Evan Rule, W.C. Haxton and Kenneth McElvain, PhysRevLett. 130 131901 (2023),(https://doi.org/10.1103/PhysRevLett.130.131901)

\[Mu2eFA\]: "Nuclear-level effective theory of Muon -> Electron Conversion: Formalism and Applications", Evan Rule, W.C. Haxton, Kenneth McElvain, and Michael J. Ramsey-Musolf, PhysRev. C 107 035504 (2023), https://doi.org/10.1103/PhysRevC.107.035504 
