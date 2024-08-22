# Malaria Simulation

This project simulates malaria cases based on weather and population data using Binomial Negative distribution.

## Prerequisites

- Python 3.x
- pandas
- numpy
- scipy 


Run the script:
```python 
python malaria_simulation.py
```
Output: simulated_malaria_data.csv


## Workflow

- Load and preprocess weather and population data
- Merge datasets
- Calculate expected malaria cases using weather variables
- Generate simulated cases using Negative Binomial distribution
- Split cases into different types (P. falciparum and P. vivax)
- Generate weekly data
- Save results to CSV

## Data sources:
- Use the data accompanied with these repository.

## Note
Adjust coefficients and parameters as needed for your specific use case.
