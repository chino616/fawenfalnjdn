# Introduction  

The file mathematica/mu2e_v2.nb is the interactive notebook.   
It will load mu2elib_v2.wl for function definitions.  mu2elib_v2.wl should remain in the same directory as mu2e_v2.nb so it can be found.

A symbolic link to mu2elib_v2.wl called Mu2eNREL.wl is maintained for use by MuonConverter.

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

# Running as a Script  

Mathematica comes with a command MathKernal that can be used to running mathematica scripts from the command line.

```
(*
 * Mathematica testing script converted from python .yaml file
 *
 * Required Setup:
 *   On Mac add /Applications/Mathematica.app/Contents/MacOS to your path to find MathKernel
 *   Set environment variable MU2E_ELASTIC to the Elastic density matrix directory
 *   Set environment variable MU2E_MATH to the directory containing mu2elib_v2.wl
 *
 * Run with:   MathKernel -script examples/Ca40Rel.wl
 *)
nbdir = Environment["MU2E_MATH"]
Get[nbdir <> "/mu2elib_v2.wl"];
(* Capture data as Mathematica association *)
data = <|
   "basefile"    -> "Ca40Rel", (* used to name plot files *)
   "isotope"     -> "40Ca",
   "interaction" -> "kbp",
   "plots"   ->  {"alsr", "atsr", "ssd", "vtmr", "vlr", "vter"},
   "mL"          -> 939.57, (* leptonic scale - using neutron mass*)
   "muonlower"   -> 1 (* Enable muon lower components *),
   "mcr"         -> 2525000.0 (* muon cap rate *),
   (* relativistic coef *)
   "ds" -> {
      {1, 0.2, 0.2},
      {2, 0.0, 1.0},
      {3, 0.1, 0.1},
      {4, 1.1, 2.1},
      {5, 0.3, 0.0},
      {6, 5.3, 5.0},
      {7, 4.3, 1.3},
      {8, -4.3, 1.3},
      {9, 4.3, -1.0},
      {10, -1.3, -1.0},
      {11, -1.3, -2.0},
      {12, -0.3, 2.7},
      {13, 0.7, 0.7},
      {14, 0.7, -0.7},
      {15, 3.7, -0.7},
      {16, 0.1, 0.2}},
   "dummy"       -> 0 (* avoid trailing comma *)
|>;

batch[data];
Quit[];
```
The response function plot names are

alsr - Axial longitudinal spin response (Sigma'')  
atsr - Axial transverse spin response (Sigma')  
ssd  - Standard spin-dependent response  
vtmr - Vector transverse magnetic response (Delta)  
vlr -  Vector longitudinal response (Phi'')  
vter - Vector transverse electric response (PhiT')  

Instead of a list, one can specify "none" or "all".  
