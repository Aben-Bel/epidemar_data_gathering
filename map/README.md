# Ethiopian Administrative Boundaries Mapping Tool

This tool allows you to create and inspect maps of different administrative levels in Ethiopia.

## Setup

1. Ensure you have Python 3.x installed.
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Files

- `aggregate_admin_levels.py`: Aggregates lower administrative levels to higher ones.
- `visualize_admin_levels.py`: Visualizes and exports data for different administrative levels.
- `map_data/`: Directory containing shapefiles and generated maps.

## Usage

### Creating Maps

Run:
```
python create_any_level_map_from_woreda.py
```

To modify:
- Change `from_level` and `to_level` in the `main()` function to aggregate different levels.

Outputs:
- New shapefile in `map_data/` (e.g., `admin1_shapes.shp`)
- PNG map (e.g., `admin1_areas.png`)

### Inspecting Maps

Run:
```
python inspect_map.py
```

To modify:
- Update shapefile paths and column names in `main()` to inspect different levels.

Outputs:
- PNG map (e.g., `ethiopia_admin1_admin3.png`)
- CSV file mapping lower to higher administrative levels (e.g., `woreda_to_region.csv`)

## Data Source

The base shapefile ET_Admin3C_2023.3.shp is sourced from FEWS NET (Famine Early Warning Systems Network). It can be found at:

https://fews.net/ethiopia-fews-net-fsc-units-2023

This dataset provides administrative boundaries for Ethiopia, including various levels of administrative divisions used for food security analysis. When using this data, please ensure to comply with FEWS NET's terms of use and provide appropriate attribution.

## Notes

- The base shapefile `ET_Admin3C_2023.3.shp` contains all administrative levels.
- Generated shapefiles and maps are saved in the `map_data/` directory.
- Modify scripts to work with different administrative levels as needed.
