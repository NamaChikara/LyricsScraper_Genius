#! python3

# LyricsScraper_Genius.py compiles a document of lyrics contained in a given
#  album page on the popular lyrics site Genius.com.

# To run this from the command line, type
#       python C:\...\LyricsScraper_Genius.py album_url output_folder
# where ... represents the path to LyricsScraper_Genius.py on your system,
# album_url is a link to an album on Genius.com, and output_folder is where
# you want the file saved to.

import requests     # for downloading the webpage HTML sources
import bs4          # for parsing the HTML
import re           # regular expressions to extract artist/album name from url
import sys          # exit in case of bad link
import os           # for file management
import webbrowser   # to open HTML document at the end
import shelve       # to store the location of a default storage directory

# --------------------------------------------------------------------------
# load album_url and destination folder for output HTML file
# --------------------------------------------------------------------------

# load .dat file that is meant to save a default directory

shelfFile = shelve.open(os.path.join(os.getcwd(), 'Destination.dat'))

if 'DIRECTORY' not in list(shelfFile.keys()):
    shelfFile['DIRECTORY'] = ''

defaultDir = shelfFile['DIRECTORY']

# attempt to load album_url and output_folder based on size of sys.argv

album_url = ''
output_folder = ''

if len(sys.argv) == 3:
    album_url = sys.argv[1]
    output_folder = sys.argv[2]
    # if the default directory is different, ask user if they would like to update it
    if defaultDir != output_folder:
        print('\n\nUpdate default save directory from\n\t%s\n--to--\n\t%s\n? (Y/N)' % (defaultDir, output_folder))
        response = input()
        if response == 'Y':
            shelfFile['DIRECTORY'] = output_folder
            print('Updated successfully.\n\n')
        elif response == 'N':
            print('Okay, it will remain the same.\n\n')
    # if there is not a default directory, initialize one
    elif not defaultDir:
        shelfFile['DIRECTORY'] = output_folder
elif len(sys.argv) == 2:
    album_url = sys.argv[1]
    # use the default directory if there is one
    if defaultDir:
        output_folder = defaultDir
    else:
        print('\n\nThere is no default save directory. Enter a path to a directory or type "EXIT".')
        response = input()
        if response == 'EXIT':
            sys.exit()
        else:
            output_folder = response
            print(response)
            shelfFile['DIRECTORY'] = output_folder
else:
    print('\n Bad number of arguments.')
    sys.exit()

# make sure folder is valid, ask user to provide a valid folder if not

if not os.path.isdir(output_folder):
    print('\nNot a valid location to save the lyrics file.')
    while True:
        print('Please enter a valid folder, "EXIT" to quit.')
        response = input()
        if response == 'EXIT':
            sys.exit()
        else:
            if os.path.isdir(response):
                output_folder = response
                break

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

titleHTML = "<h1>" + albumName.replace('-', ' ').title()
titleHTML += " by " + artistName.replace('-', ' ').title() + "</h1>"

# extract the song titles from the lyrics links

my_regex = r"^(.*?)" + re.escape(artistName) + r"-(.*?)-lyrics"
titleRegex = re.compile(my_regex)

titles = []

for link in lyricsLinks:
    songTitle = titleRegex.search(link).group(2)
    # remove dashes from the titles
    songTitle = songTitle.replace('-', ' ')
    # make title case
    songTitle = songTitle.title()
    # add header tags
    songTitle = "<h2>" + songTitle + "</h2>"
    titles.append(songTitle)
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# create an HTML document and write in the lyrics, open the result
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

# open the final HTML page

webbrowser.open(output_file)
# --------------------------------------------------------------------------
