# WhereToWatch
This project allows users to accurately find the streaming locations of movies they would like to watch.

**Link to project:** https://github.com/asriram15/DataFocusedPythonFinalProject/

**Prerequisites**
To run this application, you must have Python 3 installed and the following dependencies must be present in your environment.
You can install all necessary packages using pip:

    pip install tmdbsimple pandas

tmdbsimple: Used to search for actors and discover movies.

pandas: Used for efficient data handling and filtering of streaming sources.

tkinter: Used for the Graphical User Interface (GUI). This is usually included with standard Python installations.

The script requires two separate API keys.
    
    TMDb (The Movie Database) provides actor and movie data. 
    Register at themoviedb.org	Replace variable tmdb.API_KEY
    
    Watchmode provides streaming source data. 
    Register at api.watchmode.com	Replace variable api_key

**Running the Script**

1. Save the file (example: movielookup.py)
3. Update the API keys in the script to match yours.
4. In a terminal, run python movielookup.py

**GUI**

The script is configured to launch the Graphical User Interface (GUI) by default for the best user experience.

The GUI allows you to select the search type (Actor or Movie) from a dropdown menu.

Enter the actor's name or the movie title and click Search.

The results will show the top 5 relevant streaming sources. URLs in the results box are clickable and will open in your default web browser.

**Command-Line Interface (CLI)**

If you prefer a text-based interface, you need to change the last two lines of the script:
Change:

    if __name__ == "__main__":
        gui_main() 

To:

    if __name__ == "__main__":
        main()
When run, the CLI will prompt you to enter 1 for Actor or 2 for Movie, and then ask for the name. The results will be printed directly to the console.

**Restrictions**
Currently, the code only runs for regions in the United States. This can be adjusted by either changing the default value in beststreamingservices, or by adjusting the function calls to beststreamingservices to one of a list. The list of all available regions for this product is at https://github.com/asriram15/DataFocusedPythonFinalProject/blob/main/AvailableCountries.txt
