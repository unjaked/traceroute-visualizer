
<div align="center"></a>

# Traceroute Visualizer

### See your internet connection's journey.

![Preview](preview.png)

### Runs a `traceroute` on a domain of your choosing and generates an interactive Google Maps that shows the path your data takes to reach the domain!

<div align="left"></a>

## Dependencies

Traceroute Visualizer requires Python 3.6 or higher and the following libraries:
- `scapy` For running the traceroute.
- `requests` For getting the geolocation of an IP from a resolver.
- `gmplot` For generating the Google Maps plot of the traceroute.

Run the following Python command to install the required dependencies:</br>
```
pip install scapy requests gmplot
``` 

## Usage
Simply run the program in your terminal, with or without a commandline argument containing the URL of the domain to traceroute.

Example:
```bash
python traceroute_mapper.py google.com
```

Or simply:
```bash
python traceroute_mapper.py
```