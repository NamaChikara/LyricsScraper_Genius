# Lyrics_Scraper.py extracts the album and artist name, song titles,
#  and song lyrics from Genius.com.  This is done by passing (1) an album url
#  -or- (2) an artist page url to the function get_everything().  Depending
#  on the argument, get_everything uses the other functions in this file to
#  (1) parse the HTML from the album page to get the individual lyrics -or-
#  (2) parse the HTML from the artist page to get the album links and then
#  apply (1) for each album.

import requests     # for downloading the webpage HTML sources
import bs4          # for parsing the HTML
import re           # regular expressions to extract artist/album name from url

# --------------------------------------------------------------------------
# navigate to the album_url and extract the lyrics links on that page
# --------------------------------------------------------------------------

lyrics_regex = re.compile(r'''
                            ^(.*?)      # match any text at the beginning
                            genius.com  # make sure it is a link to genius
                            (.*?)       # any text (non-greedy)
                            -lyrics     # make sure it ends in lyrics
                            ''', re.VERBOSE)


def get_lyric_links(album_url):
    # download the webpage for the album tracklist and create a BS object
    res = requests.get(album_url)
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem accessing the album webpage (%s).' % exc)
    res_soup = bs4.BeautifulSoup(res.text, features="html.parser")

    # extract all links with class "u-display_block" (this is where song lyrics links are stored)
    link_elements = res_soup.find_all("a", "u-display_block")

    # make sure each link is actually a lyrics link before adding to link_list
    link_list = []
    for link in link_elements:
        if lyrics_regex.match(link['href']):
            link_list.append(link['href'])

    return link_list
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Extract the lyrics from each of the lyrics pages using BeautifulSoup
# --------------------------------------------------------------------------


def get_lyric_html(link_list):
    # download the webpage for each lyric and create a list of BS objects
    soup_list = []
    for link in link_list:
        res = requests.get(link)
        try:
            res.raise_for_status()
        except Exception as exc:
            print('There was a problem accessing a lyric page (%s).' % exc)
        soup_list.append(bs4.BeautifulSoup(res.text, features="html.parser"))
    return soup_list


def extract_lyrics(soup_list):
    # extract the genius-formatted lyrics
    lyrics_html = []
    for ss in soup_list:
        lyrics_html.append(ss.find("div", "lyrics"))

    # remove all <a> tags, but keep the contents
    for ll in lyrics_html:
        for tag in ll.find_all("a"):
            tag_string = ''
            for item in tag.contents:
                tag_string += str(item)
            tag.replace_with(tag_string)

    # when passing tagString to replace_with, left brackets get replaced with &lt; and right
    #  brackets by &gt;.  Before writing the lyricsHTML to file, change them to strings and apply
    #  a regular expression to return the brackets

    bracket_regex = re.compile(r'(&lt;)(.*?)(&gt;)')

    for i, ll in enumerate(lyrics_html):
        ll = str(ll)
        lyrics_html[i] = bracket_regex.sub(r'<\2>', ll)

    return lyrics_html
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Extract artist name and song titles and format for HTML document
# --------------------------------------------------------------------------

# extract artist name (to be used to extract song titles)
artist_album_regex = re.compile(r'''
                                ^(.*?)      # match any text at the beginning
                                /albums/
                                (.*?)       # artist name (non-greedy)
                                /               
                                (.*?)$      # album name 
                                ''', re.VERBOSE)


def get_names_titles(album_url, link_list):
    result = artist_album_regex.search(album_url)
    artist_name = result.group(2)
    album_name = result.group(3)

    # extract the song titles from the lyrics links
    my_regex = r"^(.*?)" + re.escape(artist_name) + r"-(.*?)-lyrics"
    title_regex = re.compile(my_regex)

    titles = []
    for link in link_list:
        song_title = title_regex.search(link).group(2)
        # remove dashes from the titles
        song_title = song_title.replace('-', ' ')
        titles.append(song_title)

    # now remove dashes from the names
    artist_name = artist_name.replace('-', ' ')
    album_name = album_name.replace('-', ' ')

    return [artist_name, album_name, titles]
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Use above functions to extract artist and album name, and lyrics from a
#  link to an album
# --------------------------------------------------------------------------


def get_album_lyrics(album_url):
    link_list = get_lyric_links(album_url)

    # if no lyrics pages are found, quit the program
    if len(link_list) == 0:
        print('There were no lyrics links found.')
        return

    soup_list = get_lyric_html(link_list)

    # if all lyrics links were unsuccessful, quit the program
    if len(soup_list) == 0:
        print('None of the lyrics pages were accessible.')
        return

    lyrics_html = extract_lyrics(soup_list)

    [artist_name, album_name, titles] = get_names_titles(album_url, link_list)

    return [artist_name, album_name, titles, lyrics_html]
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# The argument is an artist's page on Genius. Extract links to all the albums.
# --------------------------------------------------------------------------


def get_album_links(artist_url):
    # download the artist's webpage and create a BS object
    res = requests.get(artist_url)
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem accessing the artist webpage (%s).' % exc)
    res_soup = bs4.BeautifulSoup(res.text, features="html.parser")

    # extract all links with class "u-display_block" (this is where album links are stored)
    link_elements = res_soup.find_all("a", r"vertical_album_card")

    album_links = []
    for link in link_elements:
        album_links.append(link['href'])

    return album_links
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# If artist_page = False, call get_album_lyrics for the url. If True,
#  extract links to all the albums on that artist's page first.
# --------------------------------------------------------------------------

def get_everything(url, artist_page=False):

    album_lyrics = []

    if artist_page:
        album_links = get_album_links(url)
        for link in album_links:
            album_data = get_album_lyrics(link)
            album_lyrics.append(album_data)
    else:
        album_data = get_album_lyrics(url)
        album_lyrics.append(album_data)
        print(album_lyrics)

    return album_lyrics
