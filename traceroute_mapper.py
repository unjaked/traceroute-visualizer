from scapy.layers.inet import socket
from scapy.layers.inet import traceroute
import requests, gmplot, sys, os, random, webbrowser

"""
Program Name: Traceroute Visualizer

Author: https://github.com/unjaked/

Description:  Performs a traceroute on a given URL, resolves the geographic
              locations of the hops, and plots the entire path on Google Maps.

Usage: `python traceroute_mapper_jacobrd.py <URL>`
   Ex: `python traceroute_mapper_jacobrd.py google.com`
"""



def main():
    """
    Initialization/Entry point of program. Program can be ran via commandline arguments or through console.

    Steps program executes:
        1. Retrieve URL from input and clean it up (removes scheme and subdirectories)

        2. Resolve the IP of the url/hostname

        3. Perform traceroute on the IP and store a list of all IPs visited

        4. Get the geo-data of each IP from the traceroute, removing any IPs with duplicate coordinates 
           (which can result from data moving around a single data center)

        5. Plots an interactive Google Maps of the traceroute and saves a .html file. 
           Includes numbered marker for each unique location visited connected by paths
    """
    try: 
        # Get URL from user (waits for console input if no commandline arg found)
        if len(sys.argv) > 1:
            user_url = sys.argv[1]
        else:
            user_url = input("\nEnter the URL to run a traceroute on (ex: google.com, github.com): ")

        # Clean up URL (strips schemes, subdirectories, etc.)
        user_url = clean_url(user_url)

        # Get the IP of the url
        url_ip = socket.gethostbyname(user_url)

        # Call get_tracert_ips() to run a traceroute and get a list of IPs
        print(f"Tracerouting '{user_url}'..."); tracert_ip_list = get_tracert_ips(url_ip)

        # Call get_geo_data_from_ip() to get a tuple of three lists of each IP and their latitude/longitude. 
        tracert_ip_list, latitudes, longitudes = get_geo_data_from_ip(tracert_ip_list)

        # Call plot_traceroute() and create plot/map of the traceroute. Outputs as .html file in same directory.
        map_name = "traceroute_map.html"
        print("Mapping traceroute..."); plot_route(tracert_ip_list, latitudes, longitudes, map_name)
        print(f"Traceroute successfully mapped and saved as '{map_name}' in '{os.getcwd()}'")

    except socket.gaierror:
        print("Invalid input or could not resolve hostname, please try again.")
        os.system('pause') # Creates "Press any key to continue . . ." prompt
    except Exception as e:
        print(f"Unexpected error occurred: {e}")



def get_tracert_ips(ip):
    """
    Runs a traceroute on an IP and returns a list of all the IPs from the traceroute

    Args:
        ip (str): IP to run a traceroute on

    Returns:
        list: All the IPs from in the traceroute
    """
    # Run trace route (`_` variable is for storing unanswered packets; not used)
    trace_res, _ = traceroute(ip,maxttl=64, verbose = 0)

    # Initialize IP list and add user's public IP to the list (for first marker)
    ip_list = []
    ip_list.append(requests.get('https://api.ipify.org').text)

    # Iterate through the sent and received packets
    for snt, rcv in trace_res:

        # Get source IP of the response (rcv) packet and add it to the list
        src_ip = rcv.src
        ip_list.append(src_ip)

        # If source IP of response packet is the same as IP we are tracerouting, traceroute is finished. 
        # traceroute() by default repeats until maxttl=64 is reached, so this prevents excessively long lists.
        if src_ip == ip: 
            break
    
    return ip_list



def get_geo_data_from_ip(ip_list):
    """
    Resolves the geo data of a list of IP addresses in latitude and longitude, removing any IPs with duplicate coordinates.

    Args:
        ip_list (list): List of IP addresses.
    
    Returns:
        tuple: Three lists that all have corresponding indexes:
            new_ip_list (list of str): List of the original IP addresses minus any that had duplicate coordinates
            latitudes (list of float): Latitudes of each IP address.
            longitudes (list of float): Longitudes of each IP address.
    """
    # Website being used to resolve geo location from IPs
    geo_resolver = "https://dazzlepod.com/"

    # Initialize lists
    new_ip_list = []
    latitudes = []
    longitudes = []
    seen_coordinates = set()  # To track unique latitude/longitude pairs (for removing duplicates)

    # Loop through list of IPs and send a GET request to resolver to get their geo locations
    for ip in ip_list:

        # Send GET request to geo resolver (response is a JSON object)
        response = requests.get(f"{geo_resolver}/ip/{ip}.json")
        
        # Parse JSON for latitude/longitude
        if response.status_code == 200:  # Only if request succeeds
            data = response.json()  # Parses JSON response into a dictionary
            latitude = data.get("latitude")  # Gets the latitude
            longitude = data.get("longitude")  # Gets the longitude

            # Check for duplicate latitude/longitude pairs before adding to list (very unelegant solution)
            if (latitude, longitude) not in seen_coordinates:
                seen_coordinates.add((latitude, longitude))  # Add unique lat/lon pair to the set
                new_ip_list.append(ip)  # Add the corresponding IP address
                latitudes.append(latitude)  # Add the latitude to list
                longitudes.append(longitude)  # Add the longitude to list

    return new_ip_list, latitudes, longitudes



def plot_route(names, latitudes, longitudes, file_name):
    """
    Plots a traceroute on Google Maps using `gmplot` library and saves as a .html file.

    Args: 
        name (list str): List of names for each plot. Index corrosponds to latitude and longitude.
        latitudes (list float): List of latitudes. Index corrosponds to name and longitude.
        longitudes (list float): List of longitudes. Index corrosponds to name and latitude.
        file_name (str): Name of the file to save the plot to.
    """
    # Colors to use for markers
    colors = [ 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'deeppink', 
              'goldenrod', 'greenyellow', 'hotpink', 'lightseagreen', 
              'lightslategray', 'lightsteelblue', 'mediumaquamarine', 
              'orange', 'orchid', 'turquoise', 'yellowgreen']

    # Create object for generating/managing a Google Map. `(default lat, default lng, default zoom)`
    gmap = gmplot.GoogleMapPlotter(0, 0, 3) 

    # Plot the markers at coordinates
    order = 1 # For sequentially labeling each marker
    for name, lat, lon in zip(names, latitudes, longitudes):
        color = "%06x" % random.randint(0, 0xFFFFFF)
        gmap.marker(lat, lon, title=name, label=order, color=random.choice(colors))
        order += 1
    
    # Plot the paths between the coordinates
    gmap.plot(latitudes, longitudes, color='blue', edge_width=2.5)

    # Plot 'zones' at the coordinates (to demonstrate inaccuracy and approximation with geo data location)
    gmap.scatter(latitudes, longitudes, '#FF00FF', size = 30000, marker = False) 
    
    # Save the plot to a file
    gmap.draw(file_name) # Craete and save the map as an HTML into the working directory
    
    # Opens the html automatically with default browser
    cwd = os.getcwd(); webbrowser.open("file:///" + cwd + "/" + file_name)



def clean_url(url):
    """
    Strips URL to be formatted as "hostname.extension".
    Example: "https://www.google.com/" becomes "google.com"

    Args:
        url (str): URL to strip

    Returns:
        str: Stripped URL
    """
    # Strip scheme
    if url.startswith("https://"):
        url = url[8:] # Strips first 8 characters of string
    elif url.startswith("http://"):
        url = url[7:]
    
    # Strip www
    #if url.startswith("www."):
    #    url = url[4:]

    # Strip subdirectories
    url = url.split('/')[0]
    
    return url

if __name__ == "__main__":
    main()