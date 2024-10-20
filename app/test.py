import requests

# Define the parameters for the request (replace with your actual values)
year = 2024
month = 10
day = 3

# URL for the API endpoint
url = f'http://192.168.254.102:8000/get/predict/2024/10/3'

# Make the GET request
try:
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse JSON response
        print('Data:', data)
    else:
        print(f'Failed to fetch data. Status code: {response.status_code}')
except requests.exceptions.RequestException as e:
    print(f'Error occurred: {e}')
