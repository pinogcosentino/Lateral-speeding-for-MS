# Lateral-spreading-for-SM
Lateral spreading is a term used in geotechnical and earthquake engineering. It refers to the horizontal movement of soil or rock, often occurring during an earthquake. This phenomenon typically happens in areas with loose, saturated soils, and it can cause significant ground deformation, impacting structures, pipelines, and other infrastructure.
Lateral spreading usually occurs when:
- There is a liquefaction of loose, water-saturated soils.
- The ground surface slopes gently.
- There are nearby free faces, like riverbanks or sea cliffs, providing an unconfined direction for the soil to move.
This type of ground failure is especially dangerous because it can lead to the collapse of buildings, bridges, and other critical infrastructure.
Input parameters: Polygon Layer; Liquefaction Index (IL); Digital Terrain Model.
Output:Slope %; Low Susceptibility Zones; Respect Zones; Susceptibility Zones.
Examples:
The plugin identifies Zones subject to lateral spreading:
- Low Susceptibility Zones (Z0): 2 < Slope% ≤ 5 and 0 < IL ≤ 2;
- Susceptibility Zones (ZS): 2 < Slope% ≤ 5 and 2< IL ≤ 15;
- Susceptibility Zones (ZS): 5 < Slope% ≤ 15 and 0 < IL ≤ 2;
- Respect Zones (ZR): 2 < Slope% ≤ 5 and IL >15;
- Respect Zones (ZR): 2 < Slope% ≤ 15 and 2 < IL≤ 5;
- Respect Zone(ZR): Slope (%) > 15% and IL > 0.
