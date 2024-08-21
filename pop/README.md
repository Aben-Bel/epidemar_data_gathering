# Population Data Aggregation Script

This script is designed to download, inspect, and aggregate population data from WorldPop datasets for individual countries from 2000 to 2020. The script uses the WorldPop UN-adjusted population data and aggregates the population counts by administrative regions (ADMIN3) from a shapefile.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [License](#license)

## Prerequisites
- Python 3.x
- Google Colab (for running the script in the cloud)
- Google Drive (for storing data)

## Installation

1. **Install the required packages:**:
    ```bash
    pip install geopandas rasterio numpy pandas tqdm matplotlib
    ```

## Usage
1. **Mount Google Drive:**
    - In Google Colab, run the following code to mount your Google Drive:
    ```python
    from google.colab import drive
    drive.mount('/content/drive')
    ```
2. **Upload your shapefile:**
    - Upload your shapefile (e.g., ET_Admin3C_2023.3.shp) to your Google Drive.
3. **Run the script:**

    - Run the script in Google Colab or your local environment. The script will download the population data, inspect it, and aggregate the population counts by administrative regions.

4. **Check the results:**

    - The script will save the aggregated population data to a CSV file (aggregated_population.csv) in your Google Drive.

## File Structure
```
your-repo/
│
├── README.md
├── population_data/
│   ├── eth_ppp_2000_UNadj.tif
│   ├── eth_ppp_2001_UNadj.tif
│   ├── ...
│
├── ET_Admin3C_2023.3.shp
├── aggregated_population.csv
└── script.py
```

## Data Source

The base shapefile ET_Admin3C_2023.3.shp is sourced from FEWS NET (Famine Early Warning Systems Network). It can be found at:

https://fews.net/ethiopia-fews-net-fsc-units-2023

## Acknowledgments
- WorldPop for providing the population data.
- Geopandas, Rasterio, and other libraries for their excellent tools.
