# load tinyverse meta-package
library(tidyverse)
library(tm)
library(wordcloud)
library(tidytext)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the dataframe necessary for plotting word usage
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ----------------------------------------------------------
# Read in data
# ----------------------------------------------------------

# read in lyrics data and extract the Lyrics column
lyrics_df <- read_csv('C:/Users/zackb_000/Documents/Programming Projects/LyricsScraper_Genius/CSV_data/The-National_all-albums.csv')

# add a column that labels each row with a sequential ID 
#  this will be used to join lyrics_df to a DocumentTermMatrix 
#  later on
lyrics_df <- tibble::rowid_to_column(lyrics_df, "song_id")

# ----------------------------------------------------------
# Clean the lyrics of punctuation, whitespace, etc.
# ----------------------------------------------------------

# create a corpus for each lyric
lyrics_corpus <- Corpus(VectorSource(lyrics_df$Lyrics))

# function to remove html tags 
cleanTags <- function(htmlString) {
  return(gsub("<.*?>", "", htmlString))
}

# process the text (note: it may be usfull to apply
#  tm(removeWords, stopwords("english")) later depending
#  on the type of visualization that is desired)
lyrics_corpus <- lyrics_corpus %>% 
                    tm_map(cleanTags) %>%
                    tm_map(tolower) %>%
                    tm_map(removeWords, stopwords("english")) %>%
                    tm_map(removeWords, c("verse", "chorus", "prechorus")) %>%
                    tm_map(removePunctuation) %>%
                    tm_map(removeNumbers) %>%
                    tm_map(stripWhitespace)

# ----------------------------------------------------------
# create Document term matrix (i.e. a table containing the 
#  frequency of words per lyric) and left join the results
#  to lyrics_df using the tidytext package
# ----------------------------------------------------------

# In the dtm object, each row will be a lyric and each 
#  column will be a word. To examine a row of a dtm:
#  inspect(dtm[row_num,])
dtm <- DocumentTermMatrix(lyrics_corpus)

# use the tidytext package to turn the dtm into a dataframe
#  where the variables are document, term, and count (where
#  count > 0 to avoid sparsity problems)
dtm_df <- tidy(dtm)

# prepare to left joint lyrics_df to dtm_df on song_id
names(dtm_df) <- c("song_id", "word", "count")
dtm_df[,1] <- sapply(dtm_df[,1], as.integer)

lyrics_df <- lyrics_df %>% 
                left_join(dtm_df, by = "song_id") 

# remove unnecessary columns
lyrics_df <- lyrics_df %>% 
                select(c("Artist", "Album", "Song", "Year", "word", "count"))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Select desired albums for analysis and specify their years
# (optional)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

selection_on = TRUE

desired_albums = c("Alligator", "Boxer", "Cherry Tree", "High Violet", 
                   "Sad Songs For Dirty Lovers", "Sleep Well Beast", 
                   "The National", "The Virginia Ep", "Trouble Will Find Me")

desired_years = c(2005, 2007, 2004, 2010, 2003, 2017, 2001,
                  2008, 2013)

desired_df = data.frame() # built by joining desired_albums alongside desired_years
                          #  if those vectors are nonempty

if (length(desired_albums) > 0 && selection_on) {
  if (length(desired_years) > 0) {
    desired_df = data.frame(desired_albums, desired_years)
    names(desired_df) <- c("Album", "Year")
    lyrics_df <- lyrics_df %>%
      # inner_join to get rid of observations where Album %notin% desired_albums
      inner_join(desired_df, by = "Album") %>%
      # make the year column equal to desired_df%Year
      mutate(Year = Year.y) %>% 
      select(Artist, Album, Year, Song, word, count)
  }
  else {
    desired_df = data.frame(desired_albums)
    names(desired_df) <- "Album"
    lyrics_df <- lyrics_df %>%
      # inner_join to get rid of observations where Album %notin% desired_albums
      inner_join(desired_df, by = "Album") %>%
      select(Artist, Album, Year, Song, word, count)
  }
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plotting
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ----------------------------------------------------------
# set string variables for plot labels
# ----------------------------------------------------------

artist_name = lyrics_df$Artist[1]

# ----------------------------------------------------------
# create data.frame with Album and Year to refactor the x
#  aesthetic when plotting by Album in ggplot so that 
#  the plot is chronological instead of alphabetical
# ----------------------------------------------------------

album_year <- lyrics_df %>%
  distinct(Album, .keep_all = TRUE) %>%
  select(Album, Year) %>%
  arrange(Year)

# ----------------------------------------------------------
# plot the most used words 
# ----------------------------------------------------------

# set the number of times a word needs to be used to plot it
cutoff_count = 60

lyrics_df %>%
  # count word occurences; filter on cutoff_count
  group_by(word) %>%
  mutate(total_count = sum(count)) %>%
  filter(total_count >= cutoff_count) %>%
  ungroup() %>%
  # reorder in terms of total_count 
  mutate(word = reorder(word, total_count)) %>%
  ggplot(aes(x = word, y = count, fill = Album)) +
  geom_col() +
  coord_flip() +
  xlab("Word") + 
  ylab("Total uses") +
  ggtitle(paste(artist_name, "'s top words", sep = ''))

# ----------------------------------------------------------
# plot the most used words of at least a certain length
# ----------------------------------------------------------

# set the number of times a word needs to be used to plot it
long_cutoff_count = 25

# set how long a word needs to be to plot it
length_cutoff = 6

lyrics_df %>%
  # remove the short words
  filter(nchar(word) >= length_cutoff) %>%
  # count word occurences; filter on long_cutoff_count
  group_by(word) %>%
  mutate(total_count = sum(count)) %>%
  filter(total_count >= long_cutoff_count) %>%
  ungroup() %>%
  # reorder in terms of total_count 
  mutate(word = reorder(word, total_count)) %>%
  ggplot(aes(x = word, y = count, fill = Album)) +
  geom_col() +
  coord_flip() +
  xlab("Word") + 
  ylab("Total uses") +
  ggtitle(paste(artist_name, "'s top long words", sep = ''))

# ----------------------------------------------------------
# plot the average word length
# ----------------------------------------------------------
  
lyrics_df %>% 
  group_by(Album) %>%
  mutate(avg = sum(nchar(word) * count) / sum(count)) %>%
  distinct(Album, avg, .keep_all = TRUE) %>%
  ggplot(aes(x = factor(Album, level = album_year$Album), y = avg, fill = Album)) +
  geom_col() +
  xlab("Album") +
  ylab("Avg word length") +  
  theme(legend.position = 'none')
  

# ----------------------------------------------------------
# plot the number of unique words per album over time
# ---------------------------------------------------------- 

lyrics_df %>%
  count(Album) %>%
  left_join(album_year, by = "Album") %>%
  ggplot(aes(x = Album, y = n, color = Album)) +
  geom_point() +
  xlab("Album") +
  ylab("Distinct word count")

# ----------------------------------------------------------
# create Word Cloud based on terms accross all albums
# ----------------------------------------------------------

# # calculate frequency of each word
# freq <- colSums(as.matrix(dtm))
# 
# # convert to a data frame
# freq_df <- data.frame(word = names(freq), freq = freq)
# 
# # print(freq_df %>% arrange(desc(freq)))
# 
# wordcloud(words = freq_df$word, freq = freq_df$freq, min.freq = 11)
