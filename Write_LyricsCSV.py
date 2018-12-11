# LyricsScraper_Genius.py compiles a document of lyrics contained in a given
#  album page on the popular lyrics site Genius.com.

# To run this from the command line, type
#       python C:\...\LyricsScraper_Genius.py album_url output_folder
# where ... represents the path to LyricsScraper_Genius.py on your system,
# album_url is a link to an album on Genius.com, and output_folder is where
# you want the file saved to.

import re           # regular expressions to extract artist/album name from url
import os           # for file management
import csv          # for writing lyrics to file
import Lyrics_Scraper

# --------------------------------------------------------------------------
# load album_url and destination folder for output HTML file
# --------------------------------------------------------------------------

output_folder = r'C:\Users\zackb_000\Documents\Programming Projects\LyricsScraper_Genius\CSV_data'

url1 = r'https://genius.com/artists/The-national'

url2 = r'https://genius.com/albums/Kevin-morby/City-music'

# --------------------------------------------------------------------------
# extract lyrics data in the form of a list of lists;
#  [[artist_name, album_name, [song_titles], [song_lyrics]]]
# --------------------------------------------------------------------------

lyrics_data = Lyrics_Scraper.get_everything(url1, True)

# --------------------------------------------------------------------------
# create a CSV document with the extracted lyrics data
# --------------------------------------------------------------------------

# determine the file name and path

file_name = ''

if len(lyrics_data) == 1:
    file_name = lyrics_data[0][0].replace(' ', '-') + "_" + lyrics_data[0][1].replace(' ', '-') + ".csv"
else:
    file_name = lyrics_data[0][0].replace(' ', '-') + "_" + "all-albums" + ".csv"

output_file = os.path.join(output_folder, file_name)

# open the file and write to it
with open(output_file, 'w', newline='') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['Artist', 'Album', 'Song', 'Year', 'Lyrics'])
    for album in lyrics_data:
        artist_name = album[0]
        album_name = album[1]
        titles = album[2]
        lyrics = album[3]

        for song, lyric in zip(titles, lyrics):
            filewriter.writerow([artist_name, album_name, song, 0000, lyric])

# --------------------------------------------------------------------------
