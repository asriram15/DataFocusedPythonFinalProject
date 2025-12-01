import urllib.request
import json
from urllib.parse import urlencode
# Set your API key here

api_key = 'sg9LQTjvvNGPPEk6TGchFr1iQ2zuDKELbhunvY4I'
base_url= 'https://api.watchmode.com/v1'

def search(api_key,search_value,typef):
    #calls watchmode search api and returns results in a json format dictionary
    params ={
        'apiKey': api_key,
        'search_field': "name",
        'search_value': search_value,
        'types': typef
    }
    base_url= 'https://api.watchmode.com/v1'
    url =f"{base_url}/search/?{urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        data =json.loads(response.read().decode())
    return data

def streamingservices(api_key, title_id):
    base_url= 'https://api.watchmode.com/v1'
    #calls watchmode source api and returns a list of the streaming services
    params ={'apiKey': api_key}
    url =f"{base_url}/title/{title_id}/sources/?{urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        data =json.loads(response.read().decode())
    return data

def beststreamingservices(sources, region="US", tops=5):
    return sources[:tops]


def main():
    x = input("What would you like to search for? 1 = Actor, 2 = TV Show, 3 = Movie\n")

    if x == "1":
        type_ = "person"
        search_value = input("Enter Actor Name: ")
    elif x == "2":
        type_ = "tv"
        search_value = input("Enter TV Show Name: ")
    elif x == "3":
        type_ = "movie"
        search_value = input("Enter Movie Name: ")
    else:
        print("Invalid choice.")
        return
    
    searchresults=search(api_key,search_value,type_)
    print("\nSearch Results:")
    print(searchresults)
    if searchresults:
        sourceresults=streamingservices(api_key,searchresults['title_results'][0]['id'])
    else: sourceresults=[]
    print("\nStreaming Services:")
    print(sourceresults)
    topstreaming=beststreamingservices(sourceresults,region="US",tops=5)
    print("\nTop Streaming Services for you:")
    for s in topstreaming:
            name = s.get("name")
            service_type = s.get("type")
            fmt = s.get("format")
            price = s.get("price")
            url = s.get("web_url")
            if service_type == "sub":
                price_str = "included with subscription"
            elif service_type == "free":
                price_str = "free (ad-supported)"
            else:
                price_str = f"${price}" if price is not None else "unknown price"
            print(f"- {name} | {service_type} | {fmt} | {price_str}")
            print(f"  {url}\n")

if __name__ == "__main__":
    main()
