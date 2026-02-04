# Google Flights Web Scraper

A Python-based web scraper for Google Flights using Selenium that collects  flight information including prices, times, airlines, connections, and price relativity.

## Installation
1. **Install UV:**
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Set up the project:**
   ```bash
   # Navigate to project directory
   cd google-flights-scraper

   # Create virtual environment
   uv venv

   # Activate virtual environment
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows

   # Install dependencies
   uv sync
   ```

## Usage
### Basic
```python
from google_flights_scraper import GoogleFlightsScraper

# Initialize scraper
scraper = GoogleFlightsScraper()

# Scrape a flight
result = scraper.scrape_flight(
    departure_code='LAX',
    arrival_code='JFK',
    start_date='2026-03-15',
    end_date='2026-03-22',
    seat_class='Economy (include Basic)'
)

# Print results
import json
print(json.dumps(result, indent=2))
```

### Save to JSON File
```python
# Scrape and save to file
json_output = scraper.scrape_to_json(
    departure_code='SFO',
    arrival_code='ORD',
    start_date='2026-04-10',
    end_date='2026-04-17',
    seat_class='Business',
    output_file='flight_results.json'
)
```

### Batch Processing
```python
# Scrape multiple routes
routes = [
    ('LAX', 'JFK', '2026-03-15', '2026-03-22', 'Economy (include Basic)'),
    ('SFO', 'ORD', '2026-04-10', '2026-04-17', 'Business'),
    ('MIA', 'SEA', '2026-05-01', '2026-05-08', 'Premium economy')
]

results = []
for dep, arr, start, end, seat_class in routes:
    result = scraper.scrape_flight(dep, arr, start, end, seat_class)
    results.append(result)

# Save all results
with open('all_flights.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## Parameters
### `scrape_flight()` Parameters:
- **departure_code** (str): IATA airport code for departure (e.g., 'LAX')
- **arrival_code** (str): IATA airport code for arrival (e.g., 'JFK')
- **start_date** (str): Departure date in 'YYYY-MM-DD' format (e.g., '2026-03-15')
- **end_date** (str): Return date in 'YYYY-MM-DD' format (e.g., '2026-03-22')
- **seat_class** (str): Seat class - see options below

### Seat Class Options
**US Domestic Flights** (both airports in United States of America):
- `"Economy (include Basic)"`
- `"Economy (exclude Basic)"`
- `"Premium economy"`
- `"Business"`
- `"First"`

**International Flights** (at least one airport outside US):
- `"Economy"`
- `"Premium economy"`
- `"Business"`
- `"First"`

## Output Format
```json
{
  "inputs": {
    "departure_airport": "LAX",
    "arrival_airport": "JFK",
    "departure_date": "2026-03-15",
    "return_date": "2026-03-22",
    "seat_class": "Economy (include Basic)"
  },
  "departure_flight": {
    "airline": "United",
    "departure_time": "8:00 AM",
    "arrival_time": "4:30 PM",
    "total_duration": "5 hr 30 min",
    "num_stops": 1,
    "connection_airports": ["DEN"],
    "layover_durations": ["1 hr 15 min"],
    "price": "$250"
  },
  "return_flight": {
    "airline": "Delta",
    "departure_time": "9:15 AM",
    "arrival_time": "12:45 PM",
    "total_duration": "6 hr 30 min",
    "num_stops": 1,
    "connection_airports": ["ATL"],
    "layover_durations": ["2 hr 10 min"],
    "price": "$275"
  },
  "total_price": "$525",
  "price_relativity": "$57"
}
```

### Field Descriptions
- **inputs**: All input parameters used for the search
- **departure_flight**: Details of the outbound flight
- **return_flight**: Details of the return flight
- **airline**: Airline name
- **departure_time**: Departure time
- **arrival_time**: Arrival time
- **total_duration**: Total flight time
- **num_stops**: Number of stops (0 for nonstop)
- **connection_airports**: List of connection airport codes
- **layover_durations**: List of layover times at each connection
- **price**: Individual flight price
- **total_price**: Total price for round trip
- **price_relativity**: Price difference from typical (e.g., "$57" cheaper, "0" if typical, "NA" if not available)

## Configuration
### Adjust Wait Times
```python
scraper = GoogleFlightsScraper('airport_codes.csv')
scraper.wait_time = 45  # Increase to 45 seconds
scraper.max_retries = 2  # Increase retries to 2
```

### Run with Visible Browser (for debugging)
Modify the `_setup_driver` call in the code:
```python
self._setup_driver(headless=False)
```

## Troubleshooting
### Common Issues
1. **ChromeDriver not found**:
   - Install ChromeDriver: `pip install webdriver-manager`
   - Or download manually from https://chromedriver.chromium.org/
2. **Elements not found**:
   - Increase `wait_time`: `scraper.wait_time = 60`
   - Increase `max_retries`: `scraper.max_retries = 2`
3. **Invalid airport codes**:
   - Ensure codes exist in `airport_codes.csv`
   - Check IATA column for valid codes
4. **Date format errors**:
   - Use 'YYYY-MM-DD' format only
   - Ensure dates are in the future

## License
This scraper is for educational and personal use only. Please respect Google's Terms of Service and use responsibly.
