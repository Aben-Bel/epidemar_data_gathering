# -*- coding: utf-8 -*-
"""aggregated_population_from_raster_using_shapefile.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1x1EFouV_AL-Ja_oTrGC9-X8JacUvuRDE
"""

#!pip install rasterio
#!pip install geopandas
#!pip install requests
#!pip install tqdm

import geopandas as gpd
import rasterio
import numpy as np
from rasterio.features import rasterize
import requests
import os
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

# Function to download a file from a URL with a progress bar
def download_file(url, output_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    with open(output_path, 'wb') as file, tqdm(
        desc=output_path,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            bar.update(len(data))
            file.write(data)

# Mount Google Drive (if needed)
from google.colab import drive
drive.mount('/content/drive')

# Load the shapefile
shapefile_path = '/content/drive/MyDrive/ET_Admin3C_2023.3.shp'  # Update the path to your shapefile
shapefile = gpd.read_file(shapefile_path)

# make sure to check whether the shapefile is in (EPSG:4326)! (you can check this in qgis, properties of the layer)

# Base URL and years
base_url = 'https://data.worldpop.org/GIS/Population/Global_2000_2020/{year}/ETH/eth_ppp_{year}_UNadj.tif'
years = range(2000, 2021)

# Directory to save downloaded files
download_dir = '/content/drive/MyDrive/population_data'
os.makedirs(download_dir, exist_ok=True)

# Download population data for each year with progress bar if not already downloaded
for year in years:
    output_path = os.path.join(download_dir, f'eth_ppp_{year}_UNadj.tif')
    if not os.path.exists(output_path):
        url = base_url.format(year=year)
        download_file(url, output_path)

# Function to inspect raster data
def inspect_raster(raster_path):
    with rasterio.open(raster_path) as src:
        population_data = src.read(1)  # Read the first band
        affine = src.transform

        meta = src.meta
        print("Metadata:", meta)

        # Get the "no data" value from the metadata
        no_data_value = meta.get('nodata', None)

        if no_data_value is not None:
            # Filter out "no data" values
            population_data = np.where(population_data == no_data_value, np.nan, population_data)

        # Print summary statistics
        print(f"Summary statistics for {raster_path}:")
        print(f"Min: {np.nanmin(population_data)}")
        print(f"Max: {np.nanmax(population_data)}")
        print(f"Mean: {np.nanmean(population_data)}")
        print(f"Std Dev: {np.nanstd(population_data)}")

        # Check for negative values
        if np.any(population_data < 0):
            print("Warning: Negative values found in the population data")

        # Visualize the population data
        plt.figure(figsize=(10, 6))
        plt.imshow(population_data, cmap='viridis')
        plt.title('Population Data')
        plt.colorbar(label='Population')
        plt.show()

raster_path = '/content/drive/MyDrive/population_data/eth_ppp_2000_UNadj.tif'  # Update the path to your raster file
inspect_raster(raster_path)

# Initialize a list to store the results
results = []

# Process each year's population data with nested progress bars
for year in tqdm(years[:1], desc="Processing years"):
    population_raster_path = os.path.join(download_dir, f'eth_ppp_{year}_UNadj.tif')
    with rasterio.open(population_raster_path) as src:
        population_data = src.read(1)  # Read the first band
        affine = src.transform

        # Filter out "no data" values
        no_data_value = -99999.0
        population_data = np.where(population_data == no_data_value, 0, population_data)

    # Rasterize the shapefile
    shapes = [(geom, value) for geom, value in zip(shapefile.geometry, shapefile.index)]
    rasterized_shapefile = rasterize(shapes, out_shape=population_data.shape, fill=0, transform=affine, all_touched=True, dtype='uint32')

    # Aggregate population counts
    unique_values = np.unique(rasterized_shapefile)
    unique_values = unique_values[unique_values != 0]  # Exclude the background value

    for value in unique_values:
        mask = rasterized_shapefile == value
        popcount = np.sum(population_data[mask])
        admin3 = shapefile.loc[value, 'ADMIN3']
        admin2 = shapefile.loc[value, 'ADMIN2']
        admin1 = shapefile.loc[value, 'ADMIN1']
        fnid = shapefile.loc[value, 'FNID']
        results.append({'ADMIN3': admin3, 'year': year, 'popcount': popcount, 'ADMIN2': admin2, 'ADMIN1':admin1, 'FNID':fnid })

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Save the results to a CSV file
output_csv_path = '/content/drive/MyDrive/aggregated_population.csv'  # Update the path to save the CSV
results_df.to_csv(output_csv_path, index=False)
