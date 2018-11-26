import requests
import bs4
import re
import sys
import os


# --------------------------------------------------------------------------
# load album_url and destination folder for output HTML file
# --------------------------------------------------------------------------
album_url = 'https://genius.com/albums/Kevin-morby/Singing-saw'
output_folder = r'C:\Users\zackb_000\Documents\Programming Projects\LyricsScraper_Genius\SavedLyrics'

# make sure folder is valid

if not os.path.isdir(output_folder):
    print('Not a valid location to save the lyrics file.')
    sys.exit()
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# navigate to the album_url and extract the lyrics links on that page
# --------------------------------------------------------------------------

# download the webpage for the album tracklist and create a BS object

res = requests.get(album_url)
try:
    res.raise_for_status()
except Exception as exc:
    print('There was a problem accessing the album webpage (%s).' % exc)

resSoup = bs4.BeautifulSoup(res.text, features="html.parser")

# extract all links with class "u-display_block" (this is where song lyrics links are stored)

linkElements = resSoup.find_all("a", "u-display_block")

# make sure each link is actually a lyrics link before adding to list of lyricLinks

lyricsRegex = re.compile(r'''
                            ^(.*?)      # match any text at the beginning
                            genius.com  # make sure it is a link to genius
                            (.*?)       # any text (non-greedy)
                            -lyrics     # make sure it ends in lyrics
                            ''', re.VERBOSE)
lyricsLinks = []
for link in linkElements:
    if lyricsRegex.match(link['href']):
        lyricsLinks.append(link['href'])

# if no lyrics pages are found, quit the program

if len(lyricsLinks) == 0:
    print('There were no lyrics links found.')
    sys.exit()
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Extract the lyrics from each of the lyrics pages using BeautifulSoup
# --------------------------------------------------------------------------

# download the webpage for each lyric and create a list of BS objects

soups = []

for link in lyricsLinks:
    res = requests.get(link)
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem accessing a lyric page (%s).' % exc)
    soups.append(bs4.BeautifulSoup(res.text, features="html.parser"))

# if all lyrics links were unsuccessful, quit the program

if len(soups) == 0:
    print('None of the lyrics pages were accessible.')
    sys.exit()

# extract the genius-formatted lyrics

lyricsHTML = []

for ss in soups:
    lyricsHTML.append(ss.find("div", "lyrics"))

# remove all <a> tags, but keep the contents

for ll in lyricsHTML:
    for tag in ll.find_all("a"):
        tagString = ''
        for item in tag.contents:
            tagString += str(item)
        tag.replace_with(tagString)

# when passing tagString to replace_with, left brackets get replaced with &lt; and right
#  brackets by &gt;.  Before writing the lyricsHTML to file, change them to strings and apply
#  a regular expression to return the brackets

bracketRegex = re.compile(r'(&lt;)(.*?)(&gt;)')

final_lyricsHTML = []

for ll in lyricsHTML:
    ll = str(ll)
    final_lyricsHTML.append(bracketRegex.sub(r'<\2>', ll))
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Extract artist name and song titles and format for HTML document
# --------------------------------------------------------------------------

# extract artist name (to be used to extract song titles)

artist_albumRegex = re.compile(r'''
                                ^(.*?)      # match any text at the beginning
                                /albums/
                                (.*?)       # artist name (non-greedy)
                                /               
                                (.*?)$      # album name 
                                ''', re.VERBOSE)

result = artist_albumRegex.search(album_url)
artistName = result.group(2)
albumName = result.group(3)

titleHTML = "<h1>" + albumName.replace('-', ' ') + " by " + artistName.replace('-', ' ') + "</h1>"

# extract the song titles from the lyrics links

my_regex = r"^(.*?)" + re.escape(artistName) + r"-(.*?)-lyrics"
titleRegex = re.compile(my_regex)

titles = []

for link in lyricsLinks:
    dashed = titleRegex.search(link).group(2)
    # remove dashes from the titles
    notDashed = dashed.replace('-', ' ')
    # add header tags
    notDashed = "<h2>" + notDashed + "</h2>"
    titles.append(notDashed)
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# create an HTML document and write in the lyrics
# --------------------------------------------------------------------------

# determine the file name and path

file_name = artistName + "_" + albumName + ".html"
output_file = os.path.join(output_folder, file_name)

# open the file and write to it

HTML_file = open(output_file, 'w')

HTML_file.write(titleHTML)

for tt, ll in zip(titles, final_lyricsHTML):
    HTML_file.write(tt)
    HTML_file.write(str(ll))

HTML_file.close()
# --------------------------------------------------------------------------
