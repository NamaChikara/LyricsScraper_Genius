# load tinyverse meta-package
library(tidyverse)
library(tm)
library(wordcloud)
library(tidytext)

# read in lyrics data and extract the Lyrics column
lyrics_df <- read_csv('C:/Users/zackb_000/Documents/Programming Projects/LyricsScraper_Genius/CSV_data/Kevin-morby_all-albums.csv')

# add a column that labels each row with a sequential ID 
#  this will be used to join lyrics_df to a DocumentTermMatrix 
#  later on
lyrics_df <- tibble::rowid_to_column(lyrics_df, "song_id")

head(lyrics_df, 40)

# ----------------------------------------------------------
# Preprocessing
# ----------------------------------------------------------

# create a corpus for each lyric
lyrics_corpus <- Corpus(DataframeSouce(lyrics_df))

# function to remove html tags 
cleanTags <- function(htmlString) {
  return(gsub("<.*?>", "", htmlString))
}

# process the text
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

# use the tidytext package to turn the dtm into a datframe
#  where the variables are document, term, and count (where
#  count > 0 to avoid sparsity problems)
dtm_df <- tidy(dtm)

# prepare to left joint lyrics_df to dtm_df on song_id
names(dtm_df)[names(dtm_df) == 'document'] <- 'song_id'
dtm_df[,1] <- sapply(dtm_df[,1], as.integer)

lyrics_df <- lyrics_df %>% 
                left_join(dtm_df, by = "song_id") 

# remove unnecessary columns
lyrics_df <- lyrics_df %>% 
                select(c("Artist", "Song", "Album", "term", "count"))

head(lyrics_df)


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
# wordcloud(words = freq_df$word, freq = freq_df$freq, min.freq = 4)


