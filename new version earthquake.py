# Earthquake Data Analysis Script
# Goal: Find the location and magnitude of the strongest earthquake in the UK in the last century

import requests
import json
from datetime import datetime

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