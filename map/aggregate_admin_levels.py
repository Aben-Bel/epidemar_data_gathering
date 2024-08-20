import geopandas as gpd
import matplotlib.pyplot as plt

def load_shapefile(file_path):
    try:
        return gpd.read_file(file_path)
    except Exception as e:
        print(f"Error loading shapefile {file_path}: {e}")
        return None

def aggregate_admin_levels(gdf, from_level, to_level):
    # Ensure the column names exist
    if from_level not in gdf.columns or to_level not in gdf.columns:
        raise ValueError(f"Columns {from_level} or {to_level} not found in the GeoDataFrame")

    # Group by the target level and dissolve to create new geometries
    aggregated_shapes = gdf.dissolve(by=to_level, aggfunc='first')
    
    # Reset index to make the target level a column
    aggregated_shapes = aggregated_shapes.reset_index()
    
    return aggregated_shapes

def plot_admin_levels(gdf, level_column):
    fig, ax = plt.subplots(figsize=(15, 15))
    gdf.plot(ax=ax, edgecolor='black', alpha=0.7)
    
    # Add labels for each area
    for idx, row in gdf.iterrows():
        centroid = row.geometry.centroid
        ax.annotate(text=row[level_column], xy=(centroid.x, centroid.y),
                    xytext=(3, 3), textcoords="offset points",
                    fontsize=8, bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                    ha='center', va='center')
    
    plt.title(f"{level_column} Level Areas")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"{level_column.lower()}_areas.png", dpi=300, bbox_inches='tight')
    print(f"Map saved as {level_column.lower()}_areas.png")

def main():
    # Load shapefile
    shapefile_path = './map_data/ET_Admin3C_2023.3.shp'
    gdf = load_shapefile(shapefile_path)
    
    if gdf is None:
        print("Failed to load shapefile. Exiting.")
        return
    
    # Print data info
    print("Available columns:")
    print(gdf.columns)
    
    # Define the mapping levels
    from_level = 'ADMIN3'
    to_level = 'ADMIN1'
    
    # Aggregate to the desired level
    aggregated_shapes = aggregate_admin_levels(gdf, from_level, to_level)
    
    # Plot the new shapes
    plot_admin_levels(aggregated_shapes, to_level)
    
    # Save the new shapefile
    output_file = f"./map_data/{to_level.lower()}_shapes.shp"
    aggregated_shapes.to_file(output_file)
    print(f"New {to_level} shapefile saved as {output_file}")

if __name__ == "__main__":
    main()
