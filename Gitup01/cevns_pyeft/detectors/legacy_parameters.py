"""Reusable legacy CsI response defaults, independent of dataset installation."""
from dataclasses import dataclass

@dataclass(frozen=True)
class CsIResponseDefaults:
    quenching: tuple = (.0554628, 4.30681, -111.707, 840.384)
    gamma_a: float = .0749
    gamma_b: float = 9.56
    efficiency: tuple = (1.32045, .285979, 10.8646, -.3333)

CSI_RESPONSE_DEFAULTS = CsIResponseDefaults()
CSI_PE_EDGES = (.001,8.001,12.001,16.001,20.001,24.001,32.001,40.001,48.001,60.001)
CSI_COMPONENT_ACCEPTANCE = (('e', .848), ('mu', .997), ('mub', .848))
