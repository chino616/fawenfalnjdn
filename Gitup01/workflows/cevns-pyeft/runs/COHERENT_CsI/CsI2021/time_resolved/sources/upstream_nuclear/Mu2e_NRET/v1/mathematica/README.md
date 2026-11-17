# Introduction 
This mathematica script can be used to perform calculations for muon to electron conversion with various atomic targets.

**Note**: this README file is best viewed in a markdown viewer that supports embedded latex equations.   One such viewer is PanWriter.

*Atomic and Nuclear Physics Input*: The atomic input is derived from solving the Dirac equation in the nuclear Coulomb field, using the nuclear charge density profile described in the text; the parameters c and β were either taken directly from Ref. [55] or fit to the alternative density profiles provided in that
reference. The density profiles were determined from fits to elastic electron scattering and thus are consistent with the known charge radii of the targets. Table XI gives for each target the values of c and β we employed, as well as the resulting r.m.s. charge radius, the muon binding energy, the muon lower-
component probability, the computed Zeff that relates the muon wave function (averaged over the nuclear density, weighted by $j_0(qr)$) to the point Schr&#246;dinger density at the origin, the equivalent reduction factor R, the three-momentum transfer q,
and the computed q . The values for $E_{binding}$, $Z_{eff}$, $\mu_{eff}$
and $q_{eff}$ are embedded in the script. The atomic physics is evaluated for the principal isotope indicated in the Table, then used for all contributing isotopes.

The script includes options for 11 targets, ranging from C to Cu. The selection includes the light- and medium-mass nuclei that were employed in past μ → e conversion experiments or are under consideration for future experiments, as well as a few other common targets. As described in the text,
response function evaluation requires the one-body density matrix: knowledge of the full one-body density matrix allows one to calculate the exact many-body matrix element of any one-body operator. The shell model (SM) approximation to the density matrix truncates the many-body Hilbert space to some valence space and adopts a single-particle basis for representing the Slater determinants in that space. We use the harmonic oscillator, a choice that allows us to preserve translational invariance (as we use separable SM spaces). With this choice, all multi-pole operator single-particle matrix elements can be evaluated analytically.

# Running the Script
Typically, natural targets are used in experiments, so the script accesses density matrices for every isotope with an abundance $\gtrsim$ 0.2%, computing the corresponding responses by weighting each density matrix by the appropriate abundance. There is an option in the script, however, to compute the μ → e conversion rate for a selected single isotope, in which case the abundance for that isotope is set to unity.

The script provides a default value for the harmonic oscillator size parameter *b*, but allows the user to replace that with any desired alternative value.

*User Options*: The script gives the user various choices:
1) *Target*: Choose an option from Table XII below, giving the index starting from one of the table entry.
2) *Isotopic composition*: The default option is a natural target, in which case all isotopes with abundance $\gtrsim$ 0.2% are included, weighted by their abundances, as described above. The user has the option to instead select a single isotope.
3) *Density Matrix*: The user is prompted with a set of shell-model effective interactions. Once a choice is made, the script extracts the corresponding one-body density from a library, for use in evaluating the nuclear response functions.
4) *Oscillator Parameter*: The first entries for b in the last column of Table XII are the default values obtained from the formula &nbsp; $b = \sqrt{41.467 \over 45 \bar{A}^{-1/3} -25 \bar{A}^{-2/3}}~\mathrm{fm}$, but the user can specify another value.  (For example, the b values listed second in Table XII reproduce the experimental r.m.s. charge radius when point protons are assumed. This choice could be for consistency with the distributions used to evaluate lepton Coulomb wave functions, as these were determined from fits to measured electron scattering form factors.) Here $\overline{A}$ is the atomic mass computed for the natural isotope, and thus weighted over the abundances.
5) *Response Functions*: The user has the option to request that the calculated nuclear response functions be displayed either as analytic functions in y or as a graph. If this option is exercised, the user is queried about each of the six response functions and can chose to display any subset of them. The user is also asked to specify the isospin, with options including isoscalar, isovector, proton-only, and neutron-only couplings.
6) Relativistic or Nonrelativistic LECs: The user has the option of using the 20 relativistic operators of Table VII that arise for scalar and vector exchanges, rather than the basis of nonrel- ativistic operators.  If this option is exercised, it asks the user to specify the leptonic scale $m_L$ (in MeV) that is used in Table VII.
7) *LEC Input*: The user either inserts the relativistic LECs $\{i,\tilde{d}_i(0),\tilde{d}_i(1) \}$ or nonrelativistic LECs $\{i,\tilde{c}_i(0),\tilde{c}_i(1)\}$. Here $i$ is the operator index corresponding to the lists within this paper, and the two couplings are the isoscalar and isovector components. Relativistic LECs are immediately converted into their nonrelativistic equivalents, as in Table VII. The LECs are dimensionless, given in units of $1/v^2$. Only those LECs of interest have to be inserted: entry of a triad with $i = 0$ terminates the input. LECs can be inserted as numbers or as symbols.

The final output of the script is the μ → e conversion rate in 1/sec.

# Table XII (Isotopes)

|           |            |                |                                     |                               |                                 |       |                        |           |           |                        |
|-----------|------------|----------------|-------------------------------------|-------------------------------|---------------------------------|-------|------------------------|-----------|-----------|------------------------|
| ~Nucleus~ | $c$ (fm) | $\beta$ (fm) | $\sqrt{\langle r^2 \rangle}$(fm) | $E_\mu^\mathrm{bind}$ (MeV) |$\int_{0}^{\infty} \|F_{1s}\|^2 dr$ | Z | $Z_\mathrm{eff}$ | R | $q$ (MeV) | $q_\mathrm{eff}$ (MeV) |
|           |            |                |                                     |                               |                                 |       |                        |           |           |                        |
| $^{12}$C  | 2.215      | 0.491          | 2.505                               | 0.1000                        | 0.00047                         | 6     | 5.7030                 | 0.8587    | 105.07    | 108.40                 |
| $^{16}$O  | 2.534      | 0.514          | 2.739                               | 0.1775                        | 0.00083                         | 8     | 7.4210                 | 0.7982    | 105.11    | 109.16                 |
| $^{19}$F  | 2.580      | 0.567          | 2.904                               | 0.2242                        | 0.00104                         | 9     | 8.2298                 | 0.7646    | 105.12    | 109.44                 |
| $^{23}$Na | 2.760      | 0.543          | 2.940                               | 0.3337                        | 0.00154                         | 11    | 9.8547                 | 0.7190    | 105.07    | 110.25                 |
| $^{27}$Al | 3.070      | 0.519          | 3.062                               | 0.4630                        | 0.00211                         | 13    | 11.3086                | 0.6583    | 104.98    | 110.81                 |
| $^{28}$Si | 3.140      | 0.537          | 3.146                               | 0.5346                        | 0.00241                         | 14    | 12.0009                | 0.6299    | 104.91    | 111.03                 |
| $^{32}$S  | 3.161      | 0.578          | 3.239                               | 0.6924                        | 0.00308                         | 16    | 13.1839                | 0.5595    | 104.78    | 111.56                 |
| $^{40}$Ca | 3.621      | 0.563          | 3.499                               | 1.0585                        | 0.00453                         | 20    | 15.6916                | 0.4830    | 104.45    | 112.28                 |
| $^{48}$Ti | 3.843      | 0.588          | 3.693                               | 1.2615                        | 0.00527                         | 22    | 16.6562                | 0.4340    | 104.28    | 112.43                 |
| $^{56}$Fe | 4.111      | 0.558          | 3.800                               | 1.7182                        | 0.00690                         | 26    | 18.6028                | 0.3663    | 103.84    | 113.16                 |
| $^{63}$Cu | 4.218      | 0.596          | 3.947                               | 2.0884                        | 0.00811                         | 29    | 19.8563                | 0.3210    | 103.48    | 113.50                 |
| $^{184}$W | 6.510      | 0.535          | 5.421                               | 9.0851                        | 0.01169                         | 74    | 32.2914                | 0.0831    | 96.54     | 114.95                 |



# References  

[55] H. De Vries, C. W. De Jager, and C. De Vries, Atomic Data and Nucl. Data Tables 36, 495 (1987).