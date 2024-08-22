import pandas as pd
import numpy as np
from scipy.stats import nbinom 

# Function to load and preprocess data
def load_data():
    # Load LST data
    lst_data = pd.read_csv('Export_LST_Data_2002-01-01_2024-07-01.csv')
    lst_data = lst_data.groupby(['wid', 'woreda', 'year']).agg({
        'lst_day': 'mean',
        'lst_night': 'mean',
        'lst_mean': 'mean'
    }).reset_index()

    # Load Precipitation data
    precip_data = pd.read_csv('Export_Precip_Data_2002-01-01_2024-07-01.csv')
    precip_data = precip_data.groupby(['wid', 'woreda', 'year']).agg({
        'totprec': 'sum',
        'has_data': 'mean'  # This will give us the proportion of days with data
    }).reset_index()

    # Load Spectral data
    spectral_data = pd.read_csv('Export_Spectral_Data_2002-01-01_2024-07-01.csv')
    spectral_data = spectral_data.groupby(['wid', 'woreda', 'year']).agg({
        'ndvi': 'mean',
        'savi': 'mean',
        'evi': 'mean',
        'ndwi5': 'mean',
        'ndwi6': 'mean'
    }).reset_index()

    # Merge all weather data
    weather_data = lst_data.merge(precip_data, on=['wid', 'woreda', 'year'])
    weather_data = weather_data.merge(spectral_data, on=['wid', 'woreda', 'year'])

    # Load population data
    population_data = pd.read_csv('population_data.csv')
    population_data = population_data[['ADMIN3', 'year', 'popcount']]

    return weather_data, population_data

def safe_negative_binomial(mean, dispersion):
    if pd.isna(mean) or mean <= 0:
        return 0
    try:
        # Convert mean and dispersion to n and p parameters for negative binomial
        p = dispersion / (dispersion + mean)
        n = mean * p / (1 - p)
        return nbinom.rvs(n=n, p=p)
    except ValueError as e:
        print(f"Error with Negative Binomial distribution for mean: {mean}, dispersion: {dispersion}. Error: {e}")
        return int(mean)  # Fallback to rounding the expected value

def simulate_malaria_cases(weather_data, population_data, num_years=20):
    weather_data.rename(columns={"woreda":"ADMIN3"}, inplace=True) 
    print("Simulation started")
    
    print("Weather data sample:")
    print(weather_data.head())
    print("\nPopulation data sample:")
    print(population_data.head())
    
    print("\nUnique years in weather data:", weather_data['year'].unique())
    print("Unique years in population data:", population_data['year'].unique())
    
    print("\nUnique ADMIN3 in weather data:", weather_data['ADMIN3'].nunique())
    print("Unique ADMIN3 in population data:", population_data['ADMIN3'].nunique())
    
    # Merge weather and population data
    merged_data = pd.merge(weather_data, population_data, on=['ADMIN3', 'year'], how='inner')
    
    if merged_data.empty:
        print("\nMerged data is empty. Checking for mismatches:")
        weather_admin3 = set(weather_data['ADMIN3'])
        pop_admin3 = set(population_data['ADMIN3'])
        print("ADMIN3 in weather but not in population:", weather_admin3 - pop_admin3)
        print("ADMIN3 in population but not in weather:", pop_admin3 - weather_admin3)
        return None

    print("\nMerged data sample:")
    print(merged_data.head())

    # Define coefficients for weather variables
    coefficients = {
        'totprec': 0.002,
        'lst_day': 0.007,
        'lst_mean': 0.012,
        'lst_night': 0.006,
        'ndvi': 0.09,
        'savi': 0.09,
        'evi': 0.11,
        'ndwi5': 0.06,
        'ndwi6': 0.06
    }

    print("\nCalculating expected number of cases")
    # Calculate expected number of cases
    merged_data['expected_cases'] = merged_data['popcount'] * 0.01  # baseline 1% infection rate

    for var, coef in coefficients.items():
        # Check for NaN values before applying coefficient
        nan_count = merged_data[var].isna().sum()
        if nan_count > 0:
            print(f"Warning: {nan_count} NaN values found in {var}")
        
        merged_data['expected_cases'] *= np.exp(np.clip(coef * merged_data[var].fillna(0), -10, 10))  # Clip to avoid extreme values and fill NaN with 0
        print(f"After applying {var}: Min expected cases = {merged_data['expected_cases'].min()}, Max = {merged_data['expected_cases'].max()}")

    # Ensure expected_cases are positive and not too large
    merged_data['expected_cases'] = np.clip(merged_data['expected_cases'], 0.01, 1e6)

    print("\nFinal expected cases summary:")
    print(merged_data['expected_cases'].describe())

    print("\nGenerating Negative Binomial-distributed cases")
    # Set dispersion parameter 
    dispersion = 1.5  # This assumes the variance is 1.5 times the mean (This is randomly picked value for testing)

    # Generate Negative Binomial-distributed cases with error handling
    merged_data['simulated_cases'] = merged_data['expected_cases'].apply(lambda x: safe_negative_binomial(x, dispersion))

    print("\nSimulated cases summary:")
    print(merged_data['simulated_cases'].describe())
    print("\nChecking for NaN values in expected_cases:")
    nan_cases = merged_data[merged_data['expected_cases'].isna()]
    if not nan_cases.empty:
        print("Found NaN cases:")
        print(nan_cases)
    else:
        print("No NaN cases found in expected_cases.")

        
    print("\nSplitting cases into different types")
    # Split cases into different types (adjusted ratios)
    merged_data['Blood film P. falciparum'] = np.floor(merged_data['simulated_cases'] * 0.6).astype(int)
    merged_data['RDT P. falciparum'] = np.floor(merged_data['simulated_cases'] * 0.2).astype(int)
    merged_data['Blood film P. vivax'] = np.floor(merged_data['simulated_cases'] * 0.15).astype(int)
    merged_data['RDT P. vivax'] = np.floor(merged_data['simulated_cases'] * 0.05).astype(int)

    print("\nGenerating weekly data")
    # Generate weekly data
    weekly_data = []
    for _, row in merged_data.iterrows():
        for week in range(1, 53):
            weekly_data.append({
                'Woreda': row['ADMIN3'],
                'year': row['year'],
                'Epi-Week': week,
                'isoweek_enddate': f"{row['year']}-W{week:02d}",
                'Blood film P. falciparum': np.random.poisson(max(row['Blood film P. falciparum'] / 52, 0)),
                'RDT P. falciparum': np.random.poisson(max(row['RDT P. falciparum'] / 52, 0)),
                'Blood film P. vivax': np.random.poisson(max(row['Blood film P. vivax'] / 52, 0)),
                'RDT P. vivax': np.random.poisson(max(row['RDT P. vivax'] / 52, 0)),
            })

    return pd.DataFrame(weekly_data)

if __name__ == "__main__":
    print("STARTED RUNNING")
    weather_data, population_data = load_data()
    print("Finished loading weather and population data")

    simulated_malaria_data = simulate_malaria_cases(weather_data, population_data)

    if simulated_malaria_data is not None:
        simulated_malaria_data.to_csv('simulated_malaria_data.csv', index=False)
        print("Simulated data has been saved to 'simulated_malaria_data.csv'")
    else:
        print("Failed to generate simulated data due to merging issues.")
