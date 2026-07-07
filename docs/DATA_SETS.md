# RiskRadar Datasets

## Active Data Sources

These are the data sources currently integrated into RiskRadar's scraper pipeline.

### 1. NOAA National Weather Service (NWS) API
- **URL**: https://api.weather.gov
- **Alert Type**: Weather
- **Scraper**: `NWSScraper` (legacy)
- **Data**: Active weather alerts, warnings, watches, and advisories for the US
- **Interval**: Every 30 minutes
- **Auth**: None required

### 2. EPA AirNow API
- **URL**: https://www.airnow.gov
- **Alert Type**: Air Quality
- **Scraper**: `AirNowScraper` (legacy)
- **Data**: Real-time Air Quality Index (AQI) observations and forecasts
- **Interval**: Every 30 minutes
- **Auth**: None required

### 3. EPA Envirofacts (TRI)
- **URL**: https://enviro.epa.gov
- **Alert Type**: Pollution
- **Scraper**: `EPAScraper` (legacy)
- **Data**: Toxic Release Inventory (TRI) facility locations and chemical release data
- **Interval**: Every 60 minutes
- **Auth**: None required

### 4. NASA FIRMS (Fire Information for Resource Management System)
- **URL**: https://firms.modaps.eosdis.nasa.gov
- **Alert Type**: Wildfire
- **Scraper**: `FIRMSScraper` (legacy)
- **Data**: Near real-time active fire/hotspot data from MODIS and VIIRS satellite instruments
- **Interval**: Every 30 minutes
- **Auth**: Requires `NASA_FIRMS_MAP_KEY`

### 5. USGS Earthquake Hazards Program
- **URL**: https://earthquake.usgs.gov
- **Alert Type**: Earthquake
- **Scraper**: `GenericAPIScraper` (YAML-configured)
- **Data**: Real-time earthquake event data (magnitude, location, depth)
- **Interval**: Every 30 minutes
- **Auth**: None required

---

## Config-Driven Sources

Additional sources can be added without writing code by editing `config/sources.yaml`:

- **`api_sources`**: Standard REST APIs scraped via `GenericAPIScraper`
- **`web_sources`**: Arbitrary websites scraped via `WebScraper` (Firecrawl + LLM extraction)

---

## Reference Datasets

Potential additional data sources for future integration:

### Environmental
- **World Bank Open Data** (data.worldbank.org) — Climate, energy, and environmental indicators by country
- **UN Environment Programme** (unep.org/resources) — Global environmental reports and datasets
- **Global Carbon Project** (globalcarbonproject.org) — CO₂ and greenhouse gas emissions data

### Climate & Atmosphere
- **Berkeley Earth** (berkeleyearth.org/data) — Global temperature records and climate data
- **Copernicus Climate Change Service** (climate.copernicus.eu) — European climate monitoring
- **CO₂.Earth** (co2.earth) — Real-time atmospheric CO₂ tracking

### Land, Oceans & Biodiversity
- **Global Forest Watch** (globalforestwatch.org) — Deforestation and forest cover data
- **GBIF** (gbif.org) — Species occurrence and biodiversity datasets
- **Ocean Health Index** (oceanhealthindex.org) — Marine ecosystem health metrics

### Air & Water Quality
- **OpenAQ** (openaq.org) — Open-source, real-time global air quality data
- **World Resources Institute: Aqueduct** (wri.org/aqueduct) — Global water risk and stress data
