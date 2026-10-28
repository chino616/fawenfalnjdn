"""Numerical folding, separate from dimensionless response probabilities."""
import numpy as np


def trapezoid_weights(grid):
    grid = np.asarray(grid, float)
    if grid.ndim != 1 or grid.size < 2 or np.any(np.diff(grid) <= 0):
        raise ValueError("quadrature requires increasing 1D coordinates")
    delta = np.diff(grid)
    return np.r_[delta[0] / 2, (delta[:-1] + delta[1:]) / 2, delta[-1] / 2]


def linear_fold_weights(target, observation, binning, numerics, recoil, component_id):
    """WeightedFold in keV, containing selection once and no source/nucleus factor.

    Legacy reordering requires a positive total recoil yield. The compiler
    verifies the underlying coefficient response is positive semidefinite.
    """
    weights = trapezoid_weights(recoil)
    if numerics.strategy == "bin_probability_v1":
        probabilities = observation.bin_probabilities(target=target, recoil_keV=recoil,
                                                       binning=binning, component_id=component_id)
        if not np.array_equal(probabilities.recoil_keV, recoil):
            raise ValueError("probability recoil coordinates differ")
        if any((a.name, a.unit, a.clock) != (b.name, b.unit, b.clock) or not np.array_equal(a.edges, b.edges)
               for a, b in zip(probabilities.binning.axes, binning.axes)):
            raise ValueError("probability observation axes differ")
        return weights[:, None] * probabilities.values
    edges = binning.axes[0].edges
    samples = np.arange(edges[0], edges[-1] + .5 * numerics.observed_step, numerics.observed_step)
    response = np.array([observation.response.density(samples, float(t), target=target) for t in recoil], float)
    if response.shape != (len(recoil), len(samples)) or not np.all(np.isfinite(response)) or np.any(response < 0):
        raise ValueError("invalid detector density")
    folded = np.zeros((len(recoil), len(edges) - 1))
    for index, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
        sub = np.linspace(a, b, numerics.n_observed_bin)
        efficiency = np.asarray(observation.efficiency(sub), float)
        if efficiency.shape != sub.shape or not np.all(np.isfinite(efficiency)) or np.any((efficiency < 0) | (efficiency > 1)):
            raise ValueError("invalid efficiency probabilities")
        for row in range(len(recoil)):
            folded[row, index] = np.trapezoid(np.interp(sub, samples, response[row], left=0, right=0) * efficiency, sub)
    return weights[:, None] * folded * observation.selection.acceptance(component_id)


def legacy_density_fold(recoil_yield, target, observation, binning, numerics):
    """Preserve sample -> recoil integral -> clip -> interpolate -> efficiency.

    Intermediate per-kg normalization intentionally preserves the legacy clip
    scale. Returned values are per nucleus before component selection.
    """
    edges = binning.axes[0].edges
    step = numerics.observed_step
    samples = np.arange(edges[0], edges[-1] + 0.5 * step, step, dtype=float)
    recoil = recoil_yield.recoil_keV
    rate = recoil_yield.values_per_keV / target.nucleus_mass_kg
    density = np.empty(samples.size)
    clipped = 0
    for index, observed in enumerate(samples):
        response = np.array([float(observation.response.density(float(observed), float(t), target=target)) for t in recoil])
        if not np.all(np.isfinite(response)) or np.any(response < 0):
            raise ValueError("response density must be finite and nonnegative")
        value = float(np.trapezoid(rate * response, recoil))
        clipped += int(value < 0)
        density[index] = max(value, 0.0)
    values = []
    for a, b in zip(edges[:-1], edges[1:]):
        sub = np.linspace(a, b, numerics.n_observed_bin)
        interp = np.interp(sub, samples, density, left=0.0, right=0.0)
        efficiency = np.asarray(observation.efficiency(sub), dtype=float)
        if efficiency.shape != sub.shape or not np.all(np.isfinite(efficiency)) or np.any((efficiency < 0) | (efficiency > 1)):
            raise ValueError("efficiency must return finite probabilities on the observed grid")
        values.append(float(np.trapezoid(interp * efficiency, sub)) * target.nucleus_mass_kg)
    return np.asarray(values), {"clipped_density_nodes": clipped, "observed_grid": samples}


def probability_fold(recoil_yield, target, observation, binning):
    probabilities = observation.bin_probabilities(target=target, recoil_keV=recoil_yield.recoil_keV,
                                                  binning=binning, component_id=recoil_yield.component_id)
    if not np.array_equal(probabilities.recoil_keV, recoil_yield.recoil_keV):
        raise ValueError("folding recoil coordinates do not match probability matrix")
    if len(probabilities.binning.axes) != len(binning.axes) or any(
        (a.name, a.unit, a.clock) != (b.name, b.unit, b.clock) or not np.array_equal(a.edges, b.edges)
        for a, b in zip(probabilities.binning.axes, binning.axes)
    ):
        raise ValueError("folding bin axes do not match probability matrix")
    shape = (recoil_yield.recoil_keV.size,) + (1,) * len(binning.shape)
    return np.trapezoid(recoil_yield.values_per_keV.reshape(shape) * probabilities.values,
                        recoil_yield.recoil_keV, axis=0)
