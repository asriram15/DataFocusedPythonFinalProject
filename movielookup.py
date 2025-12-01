import urllib.request
import json
from urllib.parse import urlencode
import tmdbsimple as tmdb
import pandas as pd
tmdb.API_KEY = '601ce0cebc45b9d950b35e1f9ed2458d'
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
def find_actorID(actor_name):
    searh = tmdb.Search()
    response = searh.person(query=actor_name)
    results = response.get('results', [])
    for person in results:
        person_id = person.get('id')
        if person_id is not None:
            return(person_id)
    return None
def discover_movies_by_actor(actor_id):
    discover = tmdb.Discover()
    response = discover.movie(with_people=actor_id)
    for movie in response.get('results', []):
        search_value=movie['id']
        search_field = "tmdb_movie_id"
        params = {
        'apiKey': api_key,
        'search_field': search_field,
        'search_value': search_value}
        url = f'https://api.watchmode.com/v1/search/?{urlencode(params)}'
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(data)
            if data:
                print(f"Found Watchmode ID for movie {movie['title']}")
                x= streamingservices(api_key, data['title_results'][0]['id'])
                if x:
                    return beststreamingservices(x, region="US", tops=5)
    return []

def main():
    x = input("What would you like to search for? 1 = Actor, 2 = Movie\n")
    actor_id = None
    if x == "1":
        type_ = "person"
        search_value = input("Enter Actor Name: ")
        actor_id = find_actorID(search_value)
    elif x == "2":
        type_ = "movie"
        search_value = input("Enter Movie Name: ")
    else:
        print("Invalid choice.")
        return
    if actor_id:
        print(f"Actor ID for {search_value} is {actor_id}")
        movielist=discover_movies_by_actor(actor_id)
        streamingFormat(movielist)
        quit()
    searchresults=search(api_key,search_value,type_)
    #print("\nSearch Results:")
    #print(searchresults)
    if searchresults:
        sourceresults=streamingservices(api_key,searchresults['title_results'][0]['id'])
    else: sourceresults=[]
    #print("\nStreaming Services:")
    #print(sourceresults)
    topstreaming=beststreamingservices(sourceresults,region="US",tops=5)
    print("\nTop Streaming Services for you:")
    print(streamingFormat(topstreaming))

def streamingFormat(sources):
    for s in sources:
        if s.get("region") == "US":
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
