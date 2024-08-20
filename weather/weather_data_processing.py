import pandas as pd
from typing import List, Optional
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import seaborn as sns
import geopandas as gpd
import numpy as np

def load_csv(pattern: str) -> Optional[pd.DataFrame]:
    try:
        files = glob.glob(pattern)
        if not files:
            print(f"No files found matching pattern: {pattern}")
            return None

        return pd.read_csv(files[0])
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def load_woreda_to_region_mapping(file_path: str) -> pd.DataFrame:
    mapping_df = pd.read_csv(file_path)
    mapping_df['ADMIN3'] = mapping_df['ADMIN3'].astype(str)
    return mapping_df

def missing_data_report(df: pd.DataFrame, name: str, woreda_to_region: pd.DataFrame) -> pd.DataFrame:
    print(f"\nMissing Data Report for {name}\n")

    report_data = []

    # Overall missing values
    print("1. Overall Missing Values:")
    missing = df.isnull().sum()
    missing_percent = 100 * df.isnull().sum() / len(df)
    missing_table = pd.concat([missing, missing_percent], axis=1, keys=['Total Missing', 'Percent Missing'])
    print(missing_table)
    report_data.append(('overall', missing_table.reset_index().rename(columns={'index': 'column'})))

    # Missing data by month and year
    print("\n2. Missing Data by Month and Year:")
    df['month'] = pd.to_datetime(df['doy'].astype(int).astype(str) + '-' + df['year'].astype(int).astype(str), format='%j-%Y').dt.month
    monthly_missing = df.groupby(['year', 'month']).agg(lambda x: x.isnull().sum()).reset_index()
    print(monthly_missing)
    report_data.append(('monthly', monthly_missing))

    # Missing data by region and woreda
    print("\n3. Missing Data by Region and Woreda:")
    df = df.merge(woreda_to_region[['ADMIN3', 'ADMIN1']], left_on='woreda', right_on='ADMIN3', how='left')
    regional_missing = df.groupby(['ADMIN3', 'ADMIN1']).agg(lambda x: x.isnull().sum()).reset_index()
    print(regional_missing)
    report_data.append(('regional', regional_missing))

    # Additional analysis: Consecutive missing values
    print("\n4. Consecutive Missing Values:")
    consecutive_missing_data = []
    for column in df.columns:
        if df[column].isnull().sum() > 0:
            consecutive_missing = df[column].isnull().astype(int).groupby(df[column].notnull().astype(int).cumsum()).sum()
            max_consecutive = consecutive_missing.max()
            print(f"  {column}: Max consecutive missing values - {max_consecutive}")
            consecutive_missing_data.append({'column': column, 'max_consecutive': max_consecutive})
    consecutive_missing_df = pd.DataFrame(consecutive_missing_data)
    report_data.append(('consecutive', consecutive_missing_df))

    # Additional analysis: Correlation of missingness
    print("\n5. Correlation of Missingness:")
    missingness_corr = df.isnull().corr()
    print(missingness_corr)
    report_data.append(('correlation', missingness_corr.reset_index().melt(id_vars='index', var_name='column', value_name='correlation')))

    # Additional analysis: Missingness patterns
    print("\n6. Top Missingness Patterns:")
    missingness_patterns = df.isnull().value_counts().head().reset_index()
    missingness_patterns.columns = [*missingness_patterns.columns[:-1], 'count']
    print(missingness_patterns)
    report_data.append(('patterns', missingness_patterns))

    print("\n" + "="*50 + "\n")

    return pd.concat([data.assign(category=category) for category, data in report_data], ignore_index=True)


def plot_missing_data_time_series(df: pd.DataFrame, name: str):
    df['date'] = pd.to_datetime(df['doy'].astype(int).astype(str) + '-' + df['year'].astype(int).astype(str), format='%j-%Y')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    years = df['year'].unique()
    months = range(1, 13)

    fig, axes = plt.subplots(len(years), 1, figsize=(15, 5*len(years)), sharex=True)
    fig.suptitle(f'Missing Data Time Series - {name}', fontsize=16)

    for idx, year in enumerate(years):
        year_data = df[df['year'] == year]

        missing_percentages = []
        for month in months:
            month_data = year_data[year_data['month'] == month]
            missing_percentage = month_data.isnull().mean().mean() * 100
            missing_percentages.append(missing_percentage)

        ax = axes[idx] if len(years) > 1 else axes
        ax.plot(months, missing_percentages, marker='o')
        ax.set_ylabel('% Missing')
        ax.set_title(f'Year {year}')
        ax.grid(True)

    plt.xlabel('Month')
    plt.xticks(months)
    plt.tight_layout()

    plt.savefig(f'missing_data_time_series_{name.lower().replace(" ", "_")}.png')
    plt.close()

    print(f"Time series plot saved as missing_data_time_series_{name.lower().replace(' ', '_')}.png")


def plot_missing_data_choropleth(df: pd.DataFrame, name: str, woreda_to_region: pd.DataFrame, woredas_shapefile: str):
    # Calculate missing data percentage for each woreda
    missing_data = df.groupby('woreda').apply(
        lambda x: x.select_dtypes(include=[np.number]).isnull().mean().mean() * 100
    ).reset_index(name='Missing_Percentage')

    # Load the shapefile
    gdf = gpd.read_file(woredas_shapefile)

    # Merge the missing data with the GeoDataFrame
    gdf = gdf.merge(missing_data, left_on='ADMIN3', right_on='woreda', how='left')

    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    # Plot the choropleth with woreda borders
    gdf.plot(column='Missing_Percentage', ax=ax, legend=True, cmap='YlOrRd',
             legend_kwds={'label': 'Missing Data %', 'orientation': 'horizontal'},
             missing_kwds={'color': 'lightgrey'}, edgecolor='black', linewidth=0.5)

    ax.set_title(f'Missing Data Choropleth Map - {name}')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(f'missing_data_choropleth_{name.lower().replace(" ", "_")}.png', dpi=300)
    plt.close()

    print(f"Choropleth map saved as missing_data_choropleth_{name.lower().replace(' ', '_')}.png")

def main() -> None:
    # load weather data: lst, precip, and spectral
    lst_data = load_csv("*LST*.csv")
    precip_data = load_csv("*Precip*.csv")
    spectral_data = load_csv("*Spectral*.csv")

    data_frames: List[Optional[pd.DataFrame]] = [lst_data, precip_data, spectral_data]

    if not all(df is not None for df in data_frames):
        print("Some data failed to load. Please check the error messages above.")
        return

    # Load woreda to region mapping
    woreda_to_region = load_woreda_to_region_mapping("woreda_to_region.csv")

    print("\nLST\n")
    print(lst_data.head())

    print("\nPrecip\n")
    print(precip_data.head())

    print("\nSpectral\n")
    print(spectral_data.head())

    print("\nworeda_to_region\n")
    print(woreda_to_region.head())

    # Load shapefile
    woredas_shapefile = '../map/map_data/ET_Admin3C_2023.3.shp'

    print("\nAnalyzing Missing data\n")
    for df, name in zip(data_frames, ["LST Data", "Precipitation Data", "Spectral Data"]):
        # Generate missing data report
        report = missing_data_report(df, name, woreda_to_region)

        # Generate time series plot
        plot_missing_data_time_series(df, name)

        # Generate choropleth map
        plot_missing_data_choropleth(df, name, woreda_to_region, woredas_shapefile)

if __name__ == "__main__":
    print("Processing weather data")
    main()
