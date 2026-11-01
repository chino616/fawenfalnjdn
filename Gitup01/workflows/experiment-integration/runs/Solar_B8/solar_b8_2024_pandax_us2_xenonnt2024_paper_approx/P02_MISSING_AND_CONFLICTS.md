# Missing and conflicting inputs — Solar B8 2024 paper approximation

## Blocking inputs

| item | status | downstream owner | needed by | candidate source |
| --- | --- | --- | --- | --- |
| PandaX US2 2024 signal efficiency | MISSING | detector response | P06 | PandaX 2024 Fig.1 / matched release |
| XENONnT 2024 NR efficiency | MISSING | detector response | P06 | XENONnT 2024 analysis material |
| Xe-131 response and normalization convention | MISSING | theory/response | P04 | arXiv:2409.04703v2 Section III |
| PEANUTS exposure-averaged probabilities | MISSING | solar source | P03 | PEANUTS and paper Fig.2/3 |
| Fig.4--6 quantitative contours | MISSING | statistics/validation | P09 | author data or transparent digitization |

## Conflict retained

The phenomenology paper and the PandaX experiment publication use different paired-exposure
conventions. The US2 benchmark remains fixed at 1.04 t yr. The paired exposure is not used
and must not be silently substituted.

The XENONnT 2024 benchmark and XENONnT 2026 SR0/SR1/SR2 release are separate inputs with
possible run overlap. They must not be added as independent samples.

