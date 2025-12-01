import urllib.request
import json
from urllib.parse import urlencode
import tmdbsimple as tmdb
import pandas as pd

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

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
    # filter by region first, then take the top N
    if region:
        sources = [s for s in sources if s.get("region") == region]
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


def discover_movies_by_actor(actor_id, max_movies=5):   # 🔥 CHANGED 10 → 5
    """
    Use TMDb Discover to find movies for an actor, then map to Watchmode titles
    and get top US streaming sources for each. Returns a list of dicts:
    { 'title': ..., 'year': ..., 'sources': [...] }
    """
    discover = tmdb.Discover()
    response = discover.movie(with_people=actor_id, sort_by='popularity.desc')

    movies_info = []
    for movie in response.get('results', []):
        if len(movies_info) >= max_movies:
            break

        tmdb_movie_id = movie.get('id')
        if tmdb_movie_id is None:
            continue

        search_field = "tmdb_movie_id"
        params = {
            'apiKey': api_key,
            'search_field': search_field,
            'search_value': tmdb_movie_id
        }
        url = f'{base_url}/search/?{urlencode(params)}'
        with urllib.request.urlopen(url) as response_wm:
            data = json.loads(response_wm.read().decode())

        title_results = data.get('title_results', [])
        if not title_results:
            continue

        watchmode_id = title_results[0].get('id')
        if watchmode_id is None:
            continue

        sources = streamingservices(api_key, watchmode_id)
        if not sources:
            continue

        top_sources = beststreamingservices(sources, region="US", tops=5)

        movie_title = movie.get('title', 'Unknown title')
        release_date = movie.get('release_date') or ''
        year = release_date[:4] if release_date else 'N/A'

        movies_info.append({
            'title': movie_title,
            'year': year,
            'sources': top_sources
        })

    return movies_info


def streamingFormat(sources):
    # returns a formatted string of streaming options
    if not sources:
        return "  No streaming options found.\n"

    lines = []
    for s in sources:
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
        lines.append(f"  - {name} | {service_type} | {fmt} | {price_str}")
        lines.append(f"    {url}")
    return "\n".join(lines)


def format_actor_movies(movies_info):
    # formats up to 5 movies and their streaming options
    if not movies_info:
        return "No streaming sources found for this actor's movies.\n"

    lines = []
    for idx, movie in enumerate(movies_info, start=1):
        lines.append(f"{idx}. {movie['title']} ({movie['year']})")
        lines.append(streamingFormat(movie['sources']))
        lines.append("")  # blank line between movies
    return "\n".join(lines)


# ============ GUI-FRIENDLY WRAPPER ============

def build_result(choice, search_value):
    search_value = search_value.strip()
    if not search_value:
        return "Please enter a name or title.\n"

    if choice == "Actor":
        actor_id = find_actorID(search_value)
        if not actor_id:
            return f"No actor found for '{search_value}'.\n"

        header = [f"Actor: {search_value} (TMDb ID: {actor_id})", ""]
        movies_info = discover_movies_by_actor(actor_id, max_movies=5)  # 🔥 updated
        header.append("Top 5 movies and where to stream them:")
        header.append("")
        header.append(format_actor_movies(movies_info))
        return "\n".join(header)

    elif choice == "Movie":
        type_ = "movie"
        searchresults = search(api_key, search_value, type_)

        title_results = searchresults.get('title_results', [])
        if not title_results:
            return f"No movie found matching '{search_value}'.\n"

        first = title_results[0]
        title_id = first.get('id')
        title_name = first.get('name', 'Unknown title')
        year = first.get('year', 'N/A')

        header = [f"Top match: {title_name} ({year})", ""]

        sourceresults = streamingservices(api_key, title_id) if title_id is not None else []
        if not sourceresults:
            header.append("No streaming sources found for this title.\n")
            return "\n".join(header)

        topstreaming = beststreamingservices(sourceresults, region="US", tops=5)
        header.append("Top Streaming Services for you:")
        header.append("")
        header.append(streamingFormat(topstreaming))
        return "\n".join(header)

    else:
        return "Invalid choice.\n"


# ======================= TKINTER GUI =======================

def on_search_click():
    choice = type_var.get()
    query = title_entry.get()
    try:
        result_text = build_result(choice, query)
        results_box.delete("1.0", tk.END)
        results_box.insert(tk.END, result_text)
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


def gui_main():
    global type_var, title_entry, results_box

    root = tk.Tk()
    root.title("Streaming Lookup")

    top = ttk.Frame(root, padding=10)
    top.pack(fill="x")

    ttk.Label(top, text="Search type:").grid(row=0, column=0, sticky="w")

    type_var = tk.StringVar(value="Movie")
    type_menu = ttk.Combobox(
        top,
        textvariable=type_var,
        values=["Actor", "Movie"],
        state="readonly",
        width=10,
    )
    type_menu.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(top, text="Name / Title:").grid(row=0, column=2, padx=(15, 0))

    title_entry = ttk.Entry(top, width=40)
    title_entry.grid(row=0, column=3, padx=5, pady=5)

    search_btn = ttk.Button(top, text="Search", command=on_search_click)
    search_btn.grid(row=0, column=4, padx=10)

    results_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=25)
    results_box.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    root.mainloop()


# ==================== ORIGINAL CLI MAIN (KEPT) ====================

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
        movies_info = discover_movies_by_actor(actor_id, max_movies=5)  # 🔥 updated
        print(format_actor_movies(movies_info))
        quit()

    searchresults=search(api_key,search_value,type_)
    if searchresults:
        sourceresults=streamingservices(api_key,searchresults['title_results'][0]['id'])
    else:
        sourceresults=[]

    topstreaming=beststreamingservices(sourceresults,region="US",tops=5)
    print("\nTop Streaming Services for you:")
    print(streamingFormat(topstreaming))


if __name__ == "__main__":
    gui_main()
