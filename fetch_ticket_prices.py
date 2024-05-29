import requests

def get_flight_prices(origin, destination, date):
    api_key = "YOUR_ACTUAL_API_KEY"  # Replace with your actual API key
    url = f"https://partners.api.skyscanner.net/apiservices/browseroutes/v1.0/US/USD/en-US/{origin}/{destination}/{date}?apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    
    flights = data.get('Quotes', [])
    flight_info = []
    for flight in flights:
        price = flight.get('MinPrice')
        direct = flight.get('Direct')
        carrier = flight['OutboundLeg']['CarrierIds'][0]
        flight_info.append(f"Price: ${price}, Direct: {direct}, Carrier ID: {carrier}")
    
    return flight_info
