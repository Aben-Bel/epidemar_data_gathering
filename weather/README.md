# Weather Data Processing

This project processes weather data for Ethiopia, including Land Surface Temperature (LST), Precipitation, and Spectral data. It performs missing data analysis and generates various reports and visualizations.

## Prerequisites

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`):
  - pandas
  - matplotlib
  - seaborn
  - geopandas
  - numpy

## Data Sources

- The weather data (LST, Precipitation, and Spectral) was exported from Google Earth Engine using the script available at: [EPIDEMIA_GEE_script_v3.1.txt](https://github.com/EcoGRAPH/epidemiar-demo/blob/master/GEE/EPIDEMIA_GEE_script_v3.1.txt)
- The `woreda_to_region.csv` file contains mapping information for Ethiopian administrative regions.

## Usage

1. Ensure all required CSV files are in the same directory as the script.
2. Run the script:

```
python weather_data_processing.py
```

## Output

The script generates the following outputs:

1. Time series plots of missing data (PNG files):
   - `missing_data_time_series_lst_data.png`
   - `missing_data_time_series_precipitation_data.png`
   - `missing_data_time_series_spectral_data.png`

2. Choropleth maps of missing data (PNG files):
   - `missing_data_choropleth_lst_data.png`
   - `missing_data_choropleth_precipitation_data.png`
   - `missing_data_choropleth_spectral_data.png`

## Functions

- `load_csv`: Loads CSV files matching a given pattern.
- `load_woreda_to_region_mapping`: Loads the woreda to region mapping data.
- `missing_data_report`: Generates a comprehensive missing data report.
- `plot_missing_data_time_series`: Creates a time series plot of missing data.
- `plot_missing_data_choropleth`: Generates a choropleth map of missing data.
- `main`: Orchestrates the entire data processing and analysis workflow.

## Note

Ensure that the shapefile (`ET_Admin3C_2023.3.shp`) is present in the `../map/map_data/` directory for the choropleth map generation to work correctly.