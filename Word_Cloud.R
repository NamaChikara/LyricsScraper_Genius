# load tinyverse meta-package
library(tidyverse)
library(tm)

# read in lyrics data and extract the Lyrics column
ll <- read_csv('C:/Users/zackb_000/Documents/Programming Projects/Analysis_of_Lyrics/data/lyrics.csv')

ll_lyrics <- ll %>% select("Lyrics")


# ----------------------------------------------------------
# Preprocessing
# ----------------------------------------------------------

# create a corpus for each lyric
lyrics_corpus <- Corpus(DataframeSource(ll_lyrics))

# process the text
lyrics_corpus <- lyrics_corpus %>% 
                    tm_map(tolower) %>%
                    tm_map(removePunctuation) %>%
                    tm_map(removeWords, stopwords("english")) %>%
                    tm_map(removeNumbers) %>%
                    tm_map(stripWhitespace)

# Stem Document (stemDocument is supposed to convert all the words to their stem 
#                i.e. if there are two words like "walking" and "walked", stemDocument 
#                is supposed to convert them to the root word "walk")
# lyrics_corpus <- tm_map(lyrics_corpus, stemDocument,"english")

writeLines(as.character(lyrics_corpus[[2]]))

