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
    url =f"{base_url}/search/?{urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        data =json.loads(response.read().decode())
    return data

def streamingservices(api_key, title_id):
    #calls watchmode source api and returns a list of the streaming services
    params ={'apiKey': api_key}
    url =f"{base_url}/title/{title_id}/sources/?{urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        data =json.loads(response.read().decode())
    return data

def beststreamingservices(sources, region="US", tops=5):
    #gives the best 5 streaming services for said movie in US region
    region_sources =[s for s in sources if s.get("region") == region]
    if not region_sources:
        return []
    type_rank={
        "sub": 0,   
        "free": 1,
        "rent": 2,
        "buy": 3   
    }
    format_rank ={
        "4K": 0,
        "HD": 1,
        "SD": 2
    }
    best_per_provider ={}
    for s in region_sources:
        name = s.get("name")
        t = s.get("type")
        fmt = s.get("format", "HD")  
        price = s.get("price")

       
        norm_price =price if price is not None else 0.0

        key =(name,t)  

        sort_key = (
            type_rank.get(t, 99),
            norm_price,
            format_rank.get(fmt, 99)
        )

        if key not in best_per_provider:
            best_per_provider[key] = (sort_key, s)
        else:
            existing_key,fill= best_per_provider[key]
            if sort_key < existing_key:
                best_per_provider[key] = (sort_key, s)
    best= [v[1] for v in best_per_provider.values()]
    best.sort(
        key=lambda s: (
            type_rank.get(s.get("type"), 99),
            (s.get("price") if s.get("price") is not None else 0.0),
            format_rank.get(s.get("format", "HD"), 99)
        )
    )
    return best[:tops]


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
    sourceresults=streamingservices(api_key,searchresults['title_results'][0]['id'])
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