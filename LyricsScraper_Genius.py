import requests
import bs4
import re
import sys

# load album_url and extract artist name (to be used to extract song titles)

album_url = 'https://genius.com/albums/Adrianne-lenker/A-sides'

artistRegex = re.compile(r'''
                            ^(.*?)      # match any text at the beginning
                            /albums/
                            (.*?)       # artist name (non-greedy)
                            /(.*?)$
                            ''', re.VERBOSE)

artistName = artistRegex.search(album_url).group(2)

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

# extract the song titles from the lyrics links

my_regex = r"^(.*?)" + re.escape(artistName) + r"-(.*?)-lyrics"
titleRegex = re.compile(my_regex)

titles = []

for link in lyricsLinks:
    dashed = titleRegex.search(link).group(2)
    # remove dashes from the titles
    notDashed = dashed.replace('-', ' ')
    titles.append(notDashed)

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

finalHTML = []

for ll in lyricsHTML:
    ll = str(ll)
    finalHTML.append(bracketRegex.sub(r'<\2>', ll))

# create an HTML document and write in the lyrics

HTML_file = open(r'C:\Users\zackb_000\Documents\Programming Projects\PythonExercises\GeneratedQuizzes\AL.html', 'w')

for ll in finalHTML:
    HTML_file.write(str(ll))

HTML_file.close()
