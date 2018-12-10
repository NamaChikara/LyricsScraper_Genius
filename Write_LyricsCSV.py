import csv
import os

os.chdir(r'C:\Users\zackb_000\Documents\Programming Projects\Analysis_of_Lyrics\data')

print(os.getcwd())

# open file
with open('lyrics.csv', 'w', newline='') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['Artist', 'Song', 'Album', 'Year', 'Lyrics'])
    filewriter.writerow(['Kevin', 'City Music', 'City Music', 2017, 'Oh, that City Music \n Oh, those City Sounds. as a 23  \n house'])
    filewriter.writerow(['Ought', 'Room Inside The World', 'Desire', 2018, 'see the stain'])

