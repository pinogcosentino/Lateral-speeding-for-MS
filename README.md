# Lateral-spreading-for-SM
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14719324.svg)](https://doi.org/10.5281/zenodo.14719324)

Lateral spreading is a term used in geotechnical and earthquake engineering. It refers to the horizontal movement of soil or rock, often occurring during an earthquake. This phenomenon typically happens in areas with loose, saturated soils, and it can cause significant ground deformation, impacting structures, pipelines, and other infrastructure.
Lateral spreading usually occurs when:
- There is a liquefaction of loose, water-saturated soils.
- The ground surface slopes gently.
- There are nearby free faces, like riverbanks or sea cliffs, providing an unconfined direction for the soil to move.

This type of ground failure is especially dangerous because it can lead to the collapse of buildings, bridges, and other critical infrastructure.
Input parameters: Polygon Layer; Liquefaction Index (IL); Digital Terrain Model.
Output:Slope %; Low Susceptibility Zones; Respect Zones; Susceptibility Zones.

## Changelog

### Version 0.3
- Merged Layers: SZ0, RZ and SZ
- Numeric coding and the description of the formula in the layer table
- Style layer
- Fixed some minor issues

### Version 0.2
- Slope layer 
- Fixed solved calculation SZ
- Fixed some minor issues 

The tool calculates zones subject to lateral spreading:
# A) Low Susceptibility Zones (Z0): 
- 2 < Slope% ≤ 5 and 0 < IL ≤ 2
# B) Susceptibility Zones (SZ)
- 0< IL ≤ 2 and 5 < Slope% ≤ 15
- 2< IL ≤ 5 and 2 < Slope% > 5
- 5 < IL ≤ 15 and 2 < Slope% ≤ 5
# C) Respect Zones (RZ)
- 0< IL ≤ 2 and Slope% > 15
- 2< IL ≤ 5 and Slope% > 5
- 5< IL ≤ 15 and Slope% > 5
- IL >15 and Slope% > 2

*IL = liquefaction index

![figura](https://github.com/user-attachments/assets/031c0fb5-5557-4bfa-8c2c-7a3c6c9ca30a)

