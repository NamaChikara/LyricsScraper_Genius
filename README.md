# Lyrics Scraping and Analysis

This project contains programs for scraping song lyrics from the internet and analyzing their content for statistics such as word length and sentiment. My intent in writing this program was to increase my knowledge of data analytics packages in R such as dplyr and ggplot2, and to work on web scraping and file input/output in Python. 

### Files

* Lyrics_Scraper.py --- Extracts album name, artist name, song titles, and song lyrics from Genius.com.  If the link is to an artist page, it will search the artist page for the individual album links before searching the album pages for the individual song links.

* Write_LyricsCSV.py --- Writes the ouput from Lyrics_Scraper.py into a CSV file where each row is a unique (Artist, Album, Song, Year, Lyrisc) combination.

* Lyric_Analysis.R --- Reads in a CSV file written by Write_LyricsCSV.py, cleans the lyrics, and creates a document term matrix (i.e. a table containing the frequency of words per song) using the tm library. Tidyverse packages dplyr and ggplot2 are used to create plots of word occurences, average word length, and song sentiment. Library yarrr is used for pirateplot(), an improved bar chart that includes visualization of data density and displays the value of each data point.

* LyricsScraper_Genius.py --- The starting point for this project. A command line program that accepts a link to an album on Genius.com and a local directory location.  It navigates to the individual song pages and stores an HTML formatted lyrics sheet in the provided directory.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To run this code, you will need Python 3.7.1 and R on your. 

### Installing

* Python: https://www.python.org/downloads/
* R: https://cran.rstudio.com/

## Customizing behavior

Currently, Lyrics_Scraper.py does not yet extract the album year from the lyrics pages, nor does it yet have an option for removing live albums / expanded editions / singles from the output. This presents and issue for the lyrics analysis since included an album alongside its expanded edition will double the number of observations of the words used in those lyrics.  Additionally, not having the years included does not allow plots to be chronological.

In Lyric_Analysis.R, there is a section in which the user can (1) select which albums they would like to use for analysis; (2) update the values of the Year variable.   

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/?fromMenu) - The Python IDE used
* [RStudio](https://www.rstudio.com/products/rstudio/download/) - The R IDE used

## Contributing

Work that needs to be done:

* Lyrics_Scraper.py needs to extract the album year from the lyrics pages
* Lyrics_Scraper.py should have an option for removing live albums / expanded editions of albums
* Write_LyricsCSV.py should have a command line implementation
* Lyric_Analysis.R should include methods to compare artists' discographies

Please contact me if you are interested in contributing to this project.

## Authors

* **Zachary Barry** - [NamaChikara](https://github.com/NamaChikara)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
