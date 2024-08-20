import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os

def load_shapefile(file_path):
    try:
        return gpd.read_file(file_path)
    except Exception as e:
        print(f"Error loading shapefile {file_path}: {e}")
        return None

def plot_administrative_levels(higher_level, lower_level, higher_level_column, lower_level_column):
    try:
        fig, ax = plt.subplots(figsize=(15, 15))
        higher_level.plot(ax=ax, edgecolor='red', alpha=0.5)
        lower_level.plot(ax=ax, edgecolor='blue', alpha=0.2)

        # Add labels for each higher-level area
        for idx, row in higher_level.iterrows():
            centroid = row.geometry.centroid
            ax.annotate(text=row[higher_level_column], xy=(centroid.x, centroid.y),
                        xytext=(3, 3), textcoords="offset points",
                        fontsize=8, bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                        ha='center', va='center')

        plt.title(f"{higher_level_column} and {lower_level_column} in Ethiopia")
        plt.axis('off')  # Turn off axis
        plt.tight_layout()
        plt.savefig(f"ethiopia_{higher_level_column.lower()}_{lower_level_column.lower()}.png", dpi=300, bbox_inches='tight')
        print(f"Map saved as ethiopia_{higher_level_column.lower()}_{lower_level_column.lower()}.png")
    except Exception as e:
        print(f"Error plotting map: {e}")

def export_to_csv(lower_level, higher_level, lower_level_column, higher_level_column, filename):
    try:
        # Perform a spatial join to get the higher-level area for each lower-level area
        joined = gpd.sjoin(lower_level, higher_level, how="left", predicate="intersects")
        
        # Identify columns from lower_level (left) and higher_level (right)
        left_columns = [col for col in joined.columns if col.endswith('_left')]
        right_columns = [col for col in joined.columns if col.endswith('_right')]
        
        # Select columns to export
        columns_to_export = [
            f"{lower_level_column}_left",  # The main lower level column
            f"{higher_level_column}_right"  # The main higher level column
        ]
        
        # Add other columns from lower_level, excluding duplicates
        columns_to_export += [col for col in left_columns if col not in columns_to_export and not col.startswith(tuple(higher_level.columns))]
        
        # Add unique columns from higher_level
        columns_to_export += [col for col in right_columns if col.replace('_right', '') not in [c.replace('_left', '') for c in columns_to_export]]
        
        # Create the export dataframe
        export_df = joined[columns_to_export]
        
        # Rename columns to remove _left and _right suffixes
        rename_dict = {col: col.replace('_left', '').replace('_right', '') for col in export_df.columns}
        export_df = export_df.rename(columns=rename_dict)
        
        # Export to CSV
        export_df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        print(f"Available columns: {joined.columns}")

def main():
    # Load shapefiles
    admin1 = load_shapefile('./map_data/admin1_shapes.shp')
    admin3 = load_shapefile('./map_data/ET_Admin3C_2023.3.shp')

    if admin1 is None or admin3 is None:
        print("Failed to load one or both shapefiles. Exiting.")
        return

    # Print data info
    print("Admin1 (Region) data:")
    print(admin1.head())
    print("\nAdmin3 (Woreda) data:")
    print(admin3.head())

    print("\nAdmin1 columns:")
    print(admin1.columns)
    print("\nAdmin3 columns:")
    print(admin3.columns)

    # Plot map
    plot_administrative_levels(admin1, admin3, 'ADMIN1', 'ADMIN3')

    # Export to CSV
    filename = "woreda_to_region.csv"
    export_to_csv(admin3, admin1, 'ADMIN3', 'ADMIN1', filename)

if __name__ == "__main__":
    main()
