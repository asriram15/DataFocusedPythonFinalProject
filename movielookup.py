import urllib.request
import json
from urllib.parse import urlencode
# Set your API key here
api_key = 'BcxkQZqIQLh2xDBWWyez2trIRpnHbvh3zcPoUKyN'
x=input("What would you like to search for? 1 For Actor Name, 2 For TV Show Name, 3 for Movie\n")
if x=="1":
    type = 'person'
    search_value = input("Enter Actor Name: ")
elif x=="2":
    type = 'tv'
    search_value = input("Enter TV Show Name: ")
elif x=="3":
    type = 'movie'
    search_value = input("Enter Movie Name: ")

params = {
    'apiKey': api_key,
    'search_field': "name",
    'search_value': search_value,
    'types': type
}

url = f'https://api.watchmode.com/v1/search/?{urlencode(params)}'

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    title_id = data['title_results'][0]['id']
    #print(data)
if title_id:
    print(f"Found {type} with ID: {title_id}")
else:
    print(f"No {type} found with the name '{search_value}'")
    exit()
url = f'https://api.watchmode.com/v1/title/{title_id}/sources/?apiKey={api_key}'
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    print(data)