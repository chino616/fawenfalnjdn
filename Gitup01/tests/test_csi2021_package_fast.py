"""Package-specific 22-operator coefficient kernels, flavors and cache boundaries."""
from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest

from cevns_pyeft.contracts.parameters import TheoryPoint, StateParameters
from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment, ISOTOPES
from cevns_pyeft.experiments.runtime import predict_experiment, compile_experiment
from cevns_pyeft.kernels.compiler import StaleCompiledKernelError, fast_capability
from cevns_pyeft.kernels.interface_storage import save_compiled_kernel, load_compiled_kernel
from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/"data/experiments/COHERENT_CsI/CsI2021"
SMALL={"n_er":5,"n_enu":12,"n_pe_bin":3}


def operator_point(index, include_sm=True):
    spec=LI2026_OPERATOR_SPECS[index]
    rng=np.random.default_rng(20261104+index)
    matrix=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
    if spec.lepton_number=="LNV":
        np.fill_diagonal(matrix,0.)
    else:
        matrix=(matrix+matrix.conj().T)/2
    scale={5:1e-10,6:2e-7,7:1e-6,8:1e-5}[spec.dimension]
    return TheoryPoint({spec.key:scale*matrix},include_sm=include_sm)


@pytest.fixture(scope="module")
def compiled():
    experiment=load_package_experiment(PACKAGE)
    report=fast_capability(experiment.model,numerics=experiment.executor.settings({**experiment.definition.numerical_profiles["slow"],**SMALL}))
    assert report.supported,report.reasons
    kernel=compile_experiment(experiment,numerics=SMALL)
    assert len(kernel.basis_keys)==22
    assert kernel.full_kernel.shape==(2,3,8,22,22,9)
    return experiment,kernel


@pytest.mark.parametrize("index",range(22))
def test_each_packed_operator_matches_slow_per_source_isotope_bin(compiled,index):
    experiment,kernel=compiled
    point=operator_point(index)
    slow=predict_experiment(experiment,parameters=point,numerics=SMALL).combined_prediction
    fast=predict_experiment(experiment,parameters=point,numerics=SMALL,backend="fast",kernel=kernel).combined_prediction
    pair=kernel.predict(parameters=point,representation="pair")
    for key in slow.components:
        np.testing.assert_allclose(fast.components[key],slow.components[key],rtol=1e-10,atol=1e-12)
        np.testing.assert_allclose(pair.components[key],fast.components[key],rtol=1e-12,atol=1e-12)


def test_complex_mixed_lnc_lnv_points_match(compiled):
    experiment,kernel=compiled
    coefficients={}
    for index in range(22):
        coefficients.update(operator_point(index).wc_triplets)
    for sm in [False,True]:
        point=TheoryPoint(coefficients,include_sm=sm)
        slow=predict_experiment(experiment,parameters=point,numerics=SMALL).combined_prediction
        fast=kernel.predict(parameters=point)
        for key in slow.components:
            np.testing.assert_allclose(fast.components[key],slow.components[key],rtol=1e-10,atol=1e-12)


def test_package_kernel_save_load_and_external_state_contract(compiled,tmp_path):
    experiment,kernel=compiled
    file=tmp_path/"kernel.npz"
    save_compiled_kernel(file,kernel)
    reloaded=load_compiled_kernel(file,model=experiment.model)
    point=operator_point(1)
    np.testing.assert_array_equal(reloaded.full_kernel,kernel.full_kernel)
    np.testing.assert_allclose(reloaded.predict(parameters=point).counts,kernel.predict(parameters=point).counts,rtol=1e-14)
    with pytest.raises(ValueError,match="state"):
        kernel.predict(parameters=TheoryPoint(state=StateParameters({"oscillation":1.})))


@pytest.mark.parametrize("change",["source","target","response","selection","efficiency","axis","numerics"])
def test_packed_kernel_rejects_changed_physical_dependencies(compiled,change):
    from cevns_pyeft.sources.composable import ScaledSource
    from cevns_pyeft.detectors.csi2021 import ConstantEfficiency
    from cevns_pyeft.contracts.observation import Axis,Binning
    experiment,kernel=compiled
    model=experiment.model
    numerics=kernel.numerics
    if change=="source":
        model=replace(model,source=ScaledSource(model.source,1.01))
    elif change=="target":
        parts=tuple(replace(t,number_of_nuclei=t.number_of_nuclei*1.01) for t in model.targets.isotopes)
        model=replace(model,targets=replace(model.targets,isotopes=parts,detector_mass_kg=model.targets.detector_mass_kg*1.01))
    elif change=="response":
        interaction=model.interaction
        responses=dict(interaction.packed_responses)
        responses["Cs133"]=replace(responses["Cs133"],exp_factor=-2.01)
        model=replace(model,interaction=replace(interaction,packed_responses=responses))
    elif change=="selection":
        selection=replace(model.observation.selection,values={k:v*.99 for k,v in model.observation.selection.values.items()})
        model=replace(model,observation=replace(model.observation,selection=selection))
    elif change=="efficiency":
        model=replace(model,observation=replace(model.observation,efficiency=ConstantEfficiency(.8)))
    elif change=="axis":
        axis=model.binning.axes[0]
        model=replace(model,binning=Binning((Axis(axis.name,axis.unit,axis.edges+.01),)))
    elif change=="numerics":
        numerics=replace(numerics,n_enu=numerics.n_enu+1)
    with pytest.raises((StaleCompiledKernelError,ValueError)):
        kernel.predict(model=model,numerics=numerics)

