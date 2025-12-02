import urllib.request
import json
from urllib.parse import urlencode
import tmdbsimple as tmdb
import pandas as pd

# --- AI-assisted: GUI & link handling imports (ChatGPT) ---
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import re
# --- end AI-assisted imports ---

tmdb.API_KEY = '601ce0cebc45b9d950b35e1f9ed2458d'
# Set your API key here

api_key = 'sg9LQTjvvNGPPEk6TGchFr1iQ2zuDKELbhunvY4I'
base_url = 'https://api.watchmode.com/v1'


def search(api_key, search_value, typef):
    # calls watchmode search api and returns results as a DataFrame
    params = {
        'apiKey': api_key,
        'search_field': "name",
        'search_value': search_value,
        'types': typef
    }
    base_url = 'https://api.watchmode.com/v1'
    url = f"{base_url}/search/?{urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    
    # Return as DataFrame
    title_results = data.get('title_results', [])
    if title_results:
        return pd.DataFrame(title_results)
    return pd.DataFrame()


def streamingservices(api_key, title_id):
    base_url = 'https://api.watchmode.com/v1'
    # calls watchmode source api and returns streaming services as a DataFrame
    params = {'apiKey': api_key}
    url = f"{base_url}/title/{title_id}/sources/?{urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    
    # Return as DataFrame
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame()


# --- AI-assisted: region filtering & top-N selection logic (ChatGPT) ---
def beststreamingservices(sources_df: pd.DataFrame, region="US", tops=5) -> pd.DataFrame:
    # filter by region first, then take the top N rows of the DataFrame
    if sources_df.empty:
        return sources_df
    
    if region:
        sources_df = sources_df[sources_df['region'] == region]
        
    return sources_df.head(tops) # return a slice/copy of the DataFrame
# --- end AI-assisted section ---


def find_actorID(actor_name):
    searh = tmdb.Search()
    response = searh.person(query=actor_name)
    results = response.get('results', [])
    for person in results:
        person_id = person.get('id')
        if person_id is not None:
            return(person_id)
    return None


# --- AI-assisted: mapping actor → movies → Watchmode IDs + sources (ChatGPT) ---
def discover_movies_by_actor(actor_id, max_movies=5) -> pd.DataFrame:
    """
    Use TMDb Discover to find movies for an actor, then map to Watchmode titles
    and get top US streaming sources for each. Returns a DataFrame.
    """
    discover = tmdb.Discover()
    response = discover.movie(with_people=actor_id, sort_by='popularity.desc')

    movies_info = []
    
    # Use a set to prevent duplicate movie entries, though popularity sort helps
    seen_watchmode_ids = set() 

    for movie in response.get('results', []):
        if len(movies_info) >= max_movies:
            break

        tmdb_movie_id = movie.get('id')
        if tmdb_movie_id is None:
            continue

        # 1. Search Watchmode by TMDb ID
        params = {
            'apiKey': api_key,
            'search_field': "tmdb_movie_id",
            'search_value': tmdb_movie_id
        }
        url = f'{base_url}/search/?{urlencode(params)}'
        with urllib.request.urlopen(url) as response_wm:
            data = json.loads(response_wm.read().decode())

        title_results = data.get('title_results', [])
        if not title_results:
            continue

        watchmode_id = title_results[0].get('id')
        if watchmode_id is None or watchmode_id in seen_watchmode_ids:
            continue
            
        seen_watchmode_ids.add(watchmode_id)

        # 2. Get Streaming Sources
        sources_df = streamingservices(api_key, watchmode_id)
        if sources_df.empty:
            continue

        # 3. Get Top Sources
        top_sources_df = beststreamingservices(sources_df, region="US", tops=5)

        movie_title = movie.get('title', 'Unknown title')
        release_date = movie.get('release_date') or ''
        year = release_date[:4] if release_date else 'N/A'

        movies_info.append({
            'title': movie_title,
            'year': year,
            # Store the top sources DataFrame directly in the cell
            'sources_df': top_sources_df 
        })

    return pd.DataFrame(movies_info)
# --- end AI-assisted section ---


def streamingFormat(sources_df: pd.DataFrame):
    # returns a formatted string of streaming options from a DataFrame
    if sources_df.empty:
        return "  No streaming options found.\n"

    lines = []
    
    # Iterate over DataFrame rows (a clean way to handle records)
    for index, s in sources_df.iterrows():
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


# --- AI-assisted: formatting actor’s movies with streaming results (ChatGPT) ---
def format_actor_movies(movies_df: pd.DataFrame):
    # formats up to 5 movies and their streaming options from a DataFrame
    if movies_df.empty:
        return "No streaming sources found for this actor's movies.\n"

    lines = []
    # Iterate over the rows of the movies DataFrame
    for idx, movie in movies_df.iterrows():
        # idx is 0-based, so add 1 for display
        lines.append(f"{idx+1}. {movie['title']} ({movie['year']})") 
        # Pass the nested sources DataFrame to the formatter
        lines.append(streamingFormat(movie['sources_df'])) 
        lines.append("")
        
    return "\n".join(lines)
# --- end AI-assisted section ---


# ============ GUI WRAPPER ============
# --- AI-assisted: GUI-facing wrapper for search logic (ChatGPT) ---
def build_result(choice, search_value):
    search_value = search_value.strip()
    if not search_value:
        return "Please enter a name or title.\n"

    if choice == "Actor":
        actor_id = find_actorID(search_value)
        if not actor_id:
            return f"No actor found for '{search_value}'.\n"

        header = [f"Actor: {search_value} (TMDb ID: {actor_id})", ""]
        # discover_movies_by_actor returns a DataFrame
        movies_df = discover_movies_by_actor(actor_id, max_movies=5) 
        header.append("Top 5 movies and where to stream them:")
        header.append("")
        # format_actor_movies accepts a DataFrame
        header.append(format_actor_movies(movies_df)) 
        return "\n".join(header)

    elif choice == "Movie":
        # search returns a DataFrame
        searchresults_df = search(api_key, search_value, "movie") 

        if searchresults_df.empty:
            return f"No movie found matching '{search_value}'.\n"

        # Access first result
        first = searchresults_df.iloc[0]
        title_id = first.get('id')
        title_name = first.get('name', 'Unknown title')
        year = first.get('year', 'N/A')

        header = [f"Top match: {title_name} ({year})", ""]

        # streamingservices returns a DataFrame
        sourceresults_df = streamingservices(api_key, title_id) 
        if sourceresults_df.empty:
            header.append("No streaming sources found for this title.\n")
            return "\n".join(header)

        topstreaming_df = beststreamingservices(sourceresults_df, region="US", tops=5) 
        header.append("Top Streaming Services for you:")
        header.append("")
        # streamingFormat accepts a DataFrame
        header.append(streamingFormat(topstreaming_df)) 
        return "\n".join(header)

    return "Invalid choice.\n"
# --- end AI-assisted section ---


# ============ CLICKABLE LINKS SUPPORT ============
# --- AI-assisted: clickable link detection & behavior (ChatGPT) ---
URL_REGEX = re.compile(r'https?://\S+')


def insert_with_links(text_widget, text):
    # Insert text into a Text/ScrolledText widget, tagging URLs as clickable links.
    text_widget.delete("1.0", tk.END)
    text_widget.link_spans = []

    pos = 0
    while True:
        match = URL_REGEX.search(text, pos)
        if not match:
            text_widget.insert(tk.END, text[pos:])
            break

        start, end = match.start(), match.end()

        # text before link
        text_widget.insert(tk.END, text[pos:start])

        url = match.group()
        start_index = text_widget.index(tk.INSERT)
        text_widget.insert(tk.END, url, ("link",))
        end_index = text_widget.index(tk.INSERT)

        text_widget.link_spans.append((start_index, end_index, url))
        pos = end


def on_link_click(event):
    # Handle clicks on tagged links and open them in the default browser.
    widget = event.widget
    index = widget.index("@%d,%d" % (event.x, event.y))

    for start, end, url in getattr(widget, "link_spans", []):
        if widget.compare(start, "<=", index) and widget.compare(index, "<", end):
            webbrowser.open(url)
            break
# --- end AI-assisted section ---


# ======================= GUI =======================
# --- AI-assisted: Tkinter UI for search & results (ChatGPT) ---
def on_search_click():
    choice = type_var.get()
    query = title_entry.get()
    try:
        result = build_result(choice, query)
        insert_with_links(results_box, result)
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


def gui_main():
    global type_var, title_entry, results_box

    root = tk.Tk()
    root.title("Streaming Lookup")

    top = ttk.Frame(root, padding=10)
    top.pack(fill="x")

    ttk.Label(top, text="Search type:").grid(row=0, column=0)

    type_var = tk.StringVar(value="Movie")
    type_menu = ttk.Combobox(
        top,
        textvariable=type_var,
        values=["Actor", "Movie"],
        state="readonly",
        width=10
    )
    type_menu.grid(row=0, column=1, padx=5)

    ttk.Label(top, text="Name / Title:").grid(row=0, column=2, padx=(15, 0))

    title_entry = ttk.Entry(top, width=40)
    title_entry.grid(row=0, column=3, padx=5)

    ttk.Button(top, text="Search", command=on_search_click).grid(row=0, column=4, padx=10)

    results_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=25)
    results_box.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    # Softer readable link color (AI-suggested)
    results_box.tag_config("link", foreground="#1E88E5", underline=1)

    results_box.bind("<Button-1>", on_link_click)

    root.mainloop()
# --- end AI-assisted GUI section ---


# ============ CLI MAIN (your original-style interface, shortened) ============
# --- AI-assisted: condensed CLI wrapper using existing functions (ChatGPT) ---
def main():
    x = input("What would you like to search for? 1 = Actor, 2 = Movie\n")
    actor_id = None
    if x == "1":
        search_value = input("Enter Actor Name: ")
        actor_id = find_actorID(search_value)
        if actor_id:
            # Passes DataFrame
            print(format_actor_movies(discover_movies_by_actor(actor_id, 5))) 
            return
    elif x == "2":
        search_value = input("Enter Movie Name: ")
    else:
        print("Invalid choice.")
        return

    # Search returns DataFrame
    searchresults_df = search(api_key, search_value, "movie") 
    
    if searchresults_df.empty:
        print(f"No movie found matching '{search_value}'.")
        return

    # Access ID from DataFrame
    first_id = searchresults_df.iloc[0]['id'] 
    
    # Streamingservices returns DataFrame
    sourceresults_df = streamingservices(api_key, first_id) 
    
    # Process DataFrames
    top_sources_df = beststreamingservices(sourceresults_df) 
    
    # Format from DataFrame
    print(streamingFormat(top_sources_df)) 
# --- end AI-assisted CLI wrapper ---


if __name__ == "__main__":
    # AI-assisted: default to GUI for better UX (ChatGPT)
    gui_main()
