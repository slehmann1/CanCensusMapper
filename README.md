## Canadian Census Mapper

Create interactive [choropleth maps](https://en.wikipedia.org/wiki/Choropleth_map) for all data from the 2021 Canadian Census.  

<p align="center">
  <img src="https://github.com/slehmann1/CanCensusMapper/blob/main/resources/AnimatedSample.gif?raw=true" />
</p>

**Try it out [here](https://samuellehmann.com/cancensus/).**

Full stack web application built with Django and PostgreSQL. Upon starting the server, data is downloaded from the [2021 Canadian Census of population](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm?Lang=E). All census characteristics can be plotted at the [geographic units](https://en.wikipedia.org/wiki/Census_geographic_units_of_Canada) of census-subdivisions, census divisions, or provinces/territories. 

**Dependencies:**

Pandas, geopandas, shapely, numpy, pytest, chart.js, bootstrap 
