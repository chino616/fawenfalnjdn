"""Stationary per-second flux + nuclei/kg + integrated mass-time model."""
from dataclasses import dataclass,asdict
from cevns_pyeft.contracts.validation import positive,plain

@dataclass(frozen=True)
class MassTimeModel:
    source: object
    target: object
    nuclei_per_kg: float
    interaction: object
    observation: object
    exposures: tuple
    binning: object
    seconds_per_day: float
    model_id: str = 'segmented_mass_time_v1'
    def __post_init__(self):
        positive(self.nuclei_per_kg,'nuclei_per_kg');positive(self.seconds_per_day,'seconds_per_day')
        object.__setattr__(self,'exposures',tuple(self.exposures))
    def describe(self):
        return {'model_id':self.model_id,'source':self.source.describe().as_dict(),
            'target_identity':asdict(self.target),'nuclei_per_kg':self.nuclei_per_kg,
            'interaction':self.interaction.describe().as_dict(),'observation':self.observation.describe().as_dict(),
            'exposures': [asdict(x) for x in self.exposures],'seconds_per_day':self.seconds_per_day,
            'binning':[{'name':a.name,'unit':a.unit,'edges':a.edges.tolist()} for a in self.binning.axes],
            'normalization':'per_second_flux_x_nuclei_per_kg_x_seconds_per_day_x_mass_time'}
