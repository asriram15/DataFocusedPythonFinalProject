Streaming Lookup Tool

This Python script is an application for finding where movies and the filmography of actors are currently available for streaming, rental, or purchase. It utilizes both the Watchmode and TMDb APIs to provide comprehensive streaming source information.

The application includes a robust Graphical User Interface (GUI) built with Tkinter, as well as a simpler Command Line Interface (CLI).

Features

Movie Search: Search for a specific movie title and receive a list of its top streaming sources (Subscription, Rental, Purchase, Free).

Actor Search: Enter an actor's name and retrieve a list of their top 5 most popular movies, along with the streaming options for each movie.

Regional Filtering: Results are automatically filtered to show US streaming sources.

Graphical User Interface (GUI): A user-friendly window allows for easy searching, selecting the search type, and viewing results.

Clickable Links (GUI): Streaming sources listed in the results are clickable and will open in your default web browser.

Requirements

The script is written in Python 3 and requires several external libraries.

Python Libraries

You can install the required libraries using pip:

pip install tmdbsimple pandas


tmdbsimple: For interacting with The Movie Database (TMDb).

pandas: Standard Library For Dataframe Management

tkinter: Standard Python library used for the GUI (usually pre-installed).

urllib.request, json, urllib.parse, webbrowser, re: Standard Python modules.

API Key Configuration

The script requires two API keys to function, which are currently hardcoded in the file. You should replace the placeholder keys with your own valid keys.

TMDb API Key: Used by the tmdbsimple library for actor and movie metadata searches.

Find the line: tmdb.API_KEY = '601ce0cebc45b9d950b35e1f9ed2458d'

Replace the string with your TMDb API key.

Watchmode API Key: Used for finding streaming sources and linking TMDb IDs to Watchmode titles.

Find the line: api_key = 'sg9LQTjvvNGPPEk6TGchFr1iQ2zuDKELbhunvY4I'

Replace the string with your Watchmode API key.

Usage

Running the Application

To run the script, execute it directly from your terminal:

python movie_lookup.py


(Note: Since the script is configured to run gui_main() by default in the if __name__ == "__main__": block, the GUI will launch automatically.)

1. Graphical User Interface (GUI)

The primary interface is the Tkinter window.

Search Type: Use the dropdown menu to select either "Actor" or "Movie."

Name / Title: Enter the full name of the actor or the movie title you are searching for.

Search Button: Click to execute the query. Results will appear in the large text box below.

Links: Clickable URLs are displayed for each streaming option, allowing you to go directly to the source's website.

2. Command Line Interface (CLI)

A simple CLI is available but is not the default execution method. To use the CLI, you would need to modify the main execution block:

Change this (around line 250):

if __name__ == "__main__":
    # AI-assisted: default to GUI for better UX (ChatGPT)
    gui_main()


to this:

if __name__ == "__main__":
    # Use CLI instead of GUI
    main()


The CLI will then prompt you to choose between Actor (1) or Movie (2) and ask for the search value. This output also has clickable links.
