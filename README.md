# Lateral-spreading-for-SM
Lateral spreading is a term used in geotechnical and earthquake engineering. It refers to the horizontal movement of soil or rock, often occurring during an earthquake. This phenomenon typically happens in areas with loose, saturated soils, and it can cause significant ground deformation, impacting structures, pipelines, and other infrastructure.
Lateral spreading usually occurs when:
- There is a liquefaction of loose, water-saturated soils.
- The ground surface slopes gently.
- There are nearby free faces, like riverbanks or sea cliffs, providing an unconfined direction for the soil to move.

This type of ground failure is especially dangerous because it can lead to the collapse of buildings, bridges, and other critical infrastructure.
Input parameters: Polygon Layer; Liquefaction Index (IL); Digital Terrain Model.
Output:Slope %; Low Susceptibility Zones; Respect Zones; Susceptibility Zones.

The tool calculates zones subject to lateral spreading:
A) Low Susceptibility Zones (Z0): 
- 2 < Slope% ≤ 5 and 0 < IL ≤ 2
B) Susceptibility Zones (SZ)
- 0< IL ≤ 2 and 5 < Slope% ≤ 15
- 2< IL ≤ 5 and 2 < Slope% > 5
- 5 < IL ≤ 15 and 2 < Slope% ≤ 5
C) Respect Zones (RZ)
- 0< IL ≤ 2 and Slope% > 15
- 2< IL ≤ 5 and Slope% > 5
- 5< IL ≤ 15 and Slope% > 5
- IL >15 and Slope% > 2

*IL = liquefaction index
