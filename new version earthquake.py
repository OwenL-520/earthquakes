# Earthquake Data Analysis Script
# Goal: Find the location and magnitude of the strongest earthquake in the UK in the last century

import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

def get_data():
    """
    Get earthquake data from USGS
    Parameters:
    - starttime: Start time (2000-01-01)
    - endtime: End time (2018-10-11) 
    - maxlatitude/minlatitude: UK latitude range (50.008°N to 58.723°N)
    - maxlongitude/minlongitude: UK longitude range (-9.756°W to 1.67°E)
    - minmagnitude: Minimum magnitude (1.0)
    - orderby: Sort by time ascending
    """
    print("Fetching earthquake data from USGS...")
    
    response = requests.get(
        "http://earthquake.usgs.gov/fdsnws/event/1/query.geojson",
        params={
            'starttime': "2000-01-01",
            "maxlatitude": "58.723",
            "minlatitude": "50.008", 
            "maxlongitude": "1.67",
            "minlongitude": "-9.756",
            "minmagnitude": "1",
            "endtime": "2018-10-11",
            "orderby": "time-asc"
        }
    )
    
    # Check if request was successful
    if response.status_code == 200:
        print("Data retrieved successfully!")
        # Parse JSON text into Python object
        data = json.loads(response.text)
        return data
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return None

def explore_data_structure(data):
    """Explore data structure"""
    print("\n=== Data Structure Analysis ===")
    print(f"Main sections in data: {list(data.keys())}")
    
    if 'metadata' in data:
        print(f"Metadata information: {data['metadata']}")
    
    if 'features' in data:
        print(f"Number of earthquake events: {len(data['features'])}")
        
        # Analyze structure of first earthquake event
        if len(data['features']) > 0:
            first_earthquake = data['features'][0]
            print(f"\nStructure of first earthquake event:")
            print(f"- Type: {first_earthquake.get('type', 'N/A')}")
            print(f"- Properties: {list(first_earthquake.get('properties', {}).keys())}")
            print(f"- Geometry: {list(first_earthquake.get('geometry', {}).keys())}")
            
            # Display detailed information of first earthquake
            properties = first_earthquake.get('properties', {})
            geometry = first_earthquake.get('geometry', {})
            
            print(f"\nDetailed information of first earthquake:")
            print(f"- Magnitude: {properties.get('mag', 'N/A')}")
            print(f"- Place: {properties.get('place', 'N/A')}")
            print(f"- Time: {properties.get('time', 'N/A')}")
            print(f"- Coordinates: {geometry.get('coordinates', 'N/A')}")

def count_earthquakes(data):
    """Get total number of earthquakes"""
    if data and 'features' in data:
        return len(data['features'])
    return 0

def get_magnitude(earthquake):
    """Get earthquake magnitude"""
    properties = earthquake.get('properties', {})
    return properties.get('mag', 0)

def get_location(earthquake):
    """Get earthquake location (latitude and longitude)"""
    geometry = earthquake.get('geometry', {})
    coordinates = geometry.get('coordinates', [])
    if len(coordinates) >= 2:
        # Return latitude and longitude (ignore altitude)
        return coordinates[1], coordinates[0]  # 纬度, 经度
    return None, None

def get_place_name(earthquake):
    """Get earthquake place name"""
    properties = earthquake.get('properties', {})
    return properties.get('place', 'Unknown')

def get_time(earthquake):
    """Get earthquake time"""
    properties = earthquake.get('properties', {})
    time_ms = properties.get('time', 0)
    if time_ms:
        # Convert millisecond timestamp to readable format
        return datetime.fromtimestamp(time_ms / 1000)
    return None

def get_maximum(data):
    """Find the magnitude and location of the strongest earthquake"""
    if not data or 'features' not in data:
        return 0, (None, None)
    
    max_magnitude = 0
    max_location = (None, None)
    max_earthquake = None
    
    for earthquake in data['features']:
        magnitude = get_magnitude(earthquake)
        if magnitude and magnitude > max_magnitude:
            max_magnitude = magnitude
            max_location = get_location(earthquake)
            max_earthquake = earthquake
    
    return max_magnitude, max_location, max_earthquake

def analyze_earthquakes(data):
    """Analyze earthquake data"""
    if not data or 'features' not in data:
        print("No data available for analysis")
        return
    
    print("\n=== Earthquake Data Analysis ===")
    
    # Statistical information
    total_earthquakes = count_earthquakes(data)
    print(f"Total number of earthquakes: {total_earthquakes}")
    
    if total_earthquakes == 0:
        print("No earthquake data found")
        return
    
    # Magnitude statistics
    magnitudes = [get_magnitude(eq) for eq in data['features'] if get_magnitude(eq) is not None]
    if magnitudes:
        print(f"Magnitude range: {min(magnitudes):.2f} - {max(magnitudes):.2f}")
        print(f"Average magnitude: {sum(magnitudes)/len(magnitudes):.2f}")
    
    # Find strongest earthquake
    max_magnitude, max_location, max_earthquake = get_maximum(data)
    
    if max_earthquake:
        print(f"\n=== Strongest Earthquake Information ===")
        print(f"Magnitude: {max_magnitude}")
        print(f"Location coordinates: Latitude {max_location[0]:.4f}°, Longitude {max_location[1]:.4f}°")
        print(f"Place name: {get_place_name(max_earthquake)}")
        print(f"Time: {get_time(max_earthquake)}")
        
        # Display top 5 strongest earthquakes
        print(f"\n=== Top 5 Strongest Earthquakes ===")
        sorted_earthquakes = sorted(data['features'], 
                                  key=lambda x: get_magnitude(x) or 0, 
                                  reverse=True)
        
        for i, earthquake in enumerate(sorted_earthquakes[:5]):
            magnitude = get_magnitude(earthquake)
            location = get_location(earthquake)
            place = get_place_name(earthquake)
            time = get_time(earthquake)
            
            print(f"{i+1}. Magnitude {magnitude:.2f} - {place} - {time}")

def compute_yearly_stats(data):
    """Compute number of earthquakes and average magnitude per year."""
    if not data or 'features' not in data:
        return pd.DataFrame(columns=['year', 'count', 'avg_mag'])

    rows = []
    for eq in data['features']:
        t = get_time(eq)
        if t is None:
            continue
        mag = get_magnitude(eq)
        # skip None magnitudes
        if mag is None:
            continue
        rows.append({'year': t.year, 'mag': mag})

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=['year', 'count', 'avg_mag'])

    grouped = df.groupby('year').agg(count=('mag', 'size'), avg_mag=('mag', 'mean')).reset_index()
    grouped = grouped.sort_values('year')
    return grouped


def plot_yearly_stats(grouped, out_image_path=None, out_csv_path=None):
    """Create and save two plots in a single figure: count per year (bar)
    and average magnitude per year (line). Saves image and optionally CSV.
    """
    if grouped is None or grouped.empty:
        print("No yearly data to plot")
        return

    # Ensure year column is integer and sorted
    grouped = grouped.copy()
    grouped['year'] = grouped['year'].astype(int)
    grouped = grouped.sort_values('year')

    years = grouped['year']
    counts = grouped['count']
    avgs = grouped['avg_mag']

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    # Capture the bar container so we can annotate values on top
    bars = ax1.bar(years, counts, color='C0', alpha=0.6, label='Count')
    ax2.plot(years, avgs, color='C1', marker='o', linewidth=2, label='Avg Magnitude')

    # Put numeric year labels on x-axis and rotate if needed
    ax1.set_xticks(years)
    ax1.set_xticklabels(years.astype(str), rotation=45)

    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of earthquakes', color='C0')
    ax2.set_ylabel('Average magnitude', color='C1')
    ax1.tick_params(axis='y', labelcolor='C0')
    ax2.tick_params(axis='y', labelcolor='C1')

    # Annotate bar values on top
    for rect in bars:
        height = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2, height + max(counts) * 0.01,
                 f'{int(height)}', ha='center', va='bottom', fontsize=8, color='black')

    ax1.set_title('Earthquake frequency and average magnitude per year')
    fig.tight_layout()

    # Show legend combining both axes
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left')

    # Save the figure to a file
    image_path = out_image_path or 'earthquake_yearly_stats.png'
    try:
        fig.savefig(image_path, dpi=200)
        print(f"Saved plot image to: {image_path}")
    except Exception as e:
        print(f"Failed to save image: {e}")

    # Optionally save the yearly data to CSV
    if out_csv_path is None:
        out_csv_path = 'yearly_stats.csv'
    try:
        grouped.to_csv(out_csv_path, index=False)
        print(f"Saved yearly stats to: {out_csv_path}")
    except Exception as e:
        print(f"Failed to save CSV: {e}")

    # Close the figure to free resources
    plt.close(fig)

def main():
    """Main function"""
    print("UK Earthquake Data Analysis")
    print("=" * 50)
    
    # Get data
    data = get_data()
    
    if data is None:
        print("Unable to retrieve data, exiting program")
        return
    
    # Explore data structure
    explore_data_structure(data)
    
    # Analyze earthquake data
    analyze_earthquakes(data)

    # New: compute and plot yearly statistics
    yearly = compute_yearly_stats(data)
    plot_yearly_stats(yearly)
    
    # Output final results
    print("\n" + "=" * 50)
    print("Final Results:")
    max_magnitude, max_location, max_earthquake = get_maximum(data)
    
    if max_earthquake:
        print(f"Strongest earthquake in the UK in the last century:")
        print(f"Magnitude: {max_magnitude}")
        print(f"Location: {get_place_name(max_earthquake)}")
        print(f"Coordinates: Latitude {max_location[0]:.4f}°, Longitude {max_location[1]:.4f}°")
        print(f"Time: {get_time(max_earthquake)}")
    else:
        print("No earthquake data found")

if __name__ == "__main__":
    main()