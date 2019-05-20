'''
Created on 17 mai 2019

@author: Niks
'''
import line6

l = line6.api("user", "password")

l.displayMyTones()

while(True):
    print("Search for tone by artist and/or song:")
    artist = raw_input("Artist (or type exit to quit): ")
    if artist == "exit":
        break
    song = raw_input("Song: ")
       
    tones = l.getTones(artist=artist, song=song, device="amplifi_tt")
       
    for i,tone in enumerate(tones):
        print("\n{0}/{1} ---------------------------------------------------\r".format(i+1, len(tones)))
        tone.display()
    