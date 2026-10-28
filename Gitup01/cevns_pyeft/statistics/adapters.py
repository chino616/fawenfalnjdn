"""Convert a validated one-dimensional event prediction at the statistics boundary."""
import numpy as np
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from .observables import observable, prediction_vector, convert_prediction_to_dataset_observable


def to_statistical_vector(prediction, *, component_id=None, target_observable=None):
    if len(prediction.axes) != 1:
        raise UnsupportedCapabilityError("joint statistical observations are not implemented")
    axis = prediction.axes[0]
    if axis.unit != "PE" or axis.name != "reconstructed PE spectrum" or prediction.unit != "events/bin":
        raise ValueError("legacy statistics requires the reconstructed PE event spectrum")
    values = prediction.counts if component_id is None else sum(
        (value for (source, _), value in prediction.components.items() if source == component_id),
        np.zeros(prediction.binning.shape))
    if component_id is not None and not any(source == component_id for source, _ in prediction.components):
        raise ValueError(f"unknown source component {component_id!r}")
    result = prediction_vector(values, observable(axis.name, "events/bin", axis.edges),
                               metadata={"model_fingerprint": prediction.model_record["model_fingerprint"],
                                         "backend": prediction.numerical_record.get("backend"),
                                         "kernel_fingerprint": prediction.numerical_record.get("kernel_fingerprint"),
                                         "source_component": component_id, "statistics_status": "legacy approximate statistics"})
    return convert_prediction_to_dataset_observable(result, target_observable) if target_observable is not None else result
