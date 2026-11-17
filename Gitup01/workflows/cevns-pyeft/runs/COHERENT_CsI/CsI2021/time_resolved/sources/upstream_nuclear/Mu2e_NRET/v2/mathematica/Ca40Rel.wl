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
   "oscb"        -> 0.0, (* harmonic osc length scale in fm.  0 -> default *)
   "plots"   ->  "none",
   "mL"          -> 1.0*10^1, (* leptonic scale *)
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
