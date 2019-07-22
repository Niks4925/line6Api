'''
Created on 10 avr. 2019

@author: Niks
'''
import sys
import requests
import json


class tone:
    
    def __init__(self, json):
        self.json = json
        
    def display(self):
        print(u"Tone name:\t{0}\r".format(self.json["name"]).encode("utf8"))
        print(u"Author:\t\t{0}\r".format(self.json["author"]).encode("utf8"))
        print(u"Guitarist:\t{0}\r".format(self.json["guitarist"]).encode("utf8"))
        print(u"Song:\t\t{0}\r".format(self.json["song"]).encode("utf8"))
        print(u"Song id:\t{0}\r".format(self.json["searched_song_id"]).encode("utf8"))
        print(u"Band:\t\t{0}\r".format(self.json["band"]).encode("utf8"))
        print(u"Amp:\t\t{0}\r".format(self.json["amp"]).encode("utf8"))
        print(u"Style:\t\t{0}\r".format(self.json["style"]))
        print(u"Comments:\t{0}\r".format(self.json["comments"]).encode("utf8"))
        print(u"Date:\t\t{0}\r".format(self.json["posted"]).encode("utf8"))
        print(u"Downloads:\t{0}\r".format(self.json["downloads"]).encode("utf8"))
        print(u"Url:\t\thttps://line6.com/customtone/tone/{0}\r".format(self.json["id"]).encode("utf8"))
    
    def getDownloadCount(self):
        return int(self.json["downloads"])
    
    def getAuthor(self):
        return self.json["author"]
    


class api:

    API_KEY = "f27e98cd2e605249b9bece6cb92d641f"
    API_ENDPOINT = "https://line6.com/api/rest/v1/"
    
    midi_id = {
        "amplifi_75": 2097153,
        "amplifi_150": 2097154,
        "amplifi_fx100": 2097155,
        "firehawk_fx": 2097156,
        "amplifi_tt": 2097157,
        "firehawk_1500": 2097158,
        "amplifi_30": 2097159}

    def __init__(self, user, password):
        """ 
        Initialize connection and get your tones and your favourites tones
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AMPLIFi Remote/2.61.0 (Android 8.0) Line6_WWW/0.1"})
        
        self.user = user
        self.password = password
        self.token = None
        
        self.myTones = []
        self.favouritesTones = []

        self.login()
        self.myTones = self.getMyTones()
        self.favouritesTones = self.getMyTones(True)
        

    def login(self):
        """"
        Login to line6 api and get session token
        """
        data = {"apikey": self.API_KEY, "user":self.user, "pass":self.password, "appname": "AMPLIFi Remote", "appver": "2.61.0"}
        r = self.session.post(self.API_ENDPOINT + "login", data=data)
        
        result = r.json()["result"]
        #print(json.dumps(result, indent=4, sort_keys=True))
        
        if result["status"] == "OK":
            self.token = result["data"]["token"]
        else:
            print(result["string"])
            sys.exit(-1)        
            

    def getTones(self, artist="", song="", genre="", device="", comp=""):
        """
        Get tones related to parameters and return results as an array of tones
        """
        
        tones = []
        d_id = self.getDeviceId(device)       
        r = self.getRequest("customtone/tones?format=json&artist={0}&song={1}&genre={2}&midi_id={3}&compatible={4}&records=30".format(artist, song, genre, d_id, comp))
        
        #print(json.dumps(r.json(), indent=4, sort_keys=True))
        
        for t in r.json()["result"]["data"]["tones"]:
            tones.append(tone(t))
        
        tones.sort(key=self.orderByDownload, reverse=True)
        return tones  
    
    def getMyTones(self, favorites=False):
        """
        Get your tones or your favorites tones and return results as an array of tones
        """
        tones = []
        
        if favorites:
            f = "1"
        else:
            f = "0"
        
        r = self.getRequest("customtone/tones?format=json&mytones=1&favorites={0}&midi_id={1}".format(f, self.getDeviceId("amplifi_tt")))
        res = r.json()
        #print(json.dumps(res, indent=4, sort_keys=True))
        
        for t in res["result"]["data"]["tones"]:
            tones.append(tone(t))
        return tones
    
    
    def displayMyTones(self, favorites=False):
        """
        Display your tones
        """
        if favorites:
            for tone in self.myTones:
                tone.display()
                print("----------------------------------")
        else:
            for tone in self.favouritesTones:
                tone.display()
                print("----------------------------------")
                
    
    def downloadTone(self, tone_id):
        """
        Download tone file content (most of a time a l6p file).
        This needs to be tested more.
        """
        r = self.getRequest("customtone/tone?format=json&id={0}".format(tone_id))
        print(r.text.encode("utf8"))
        #print(json.dumps(r.json(), indent=4, sort_keys=True))
          
    def uploadTone(self, toneData):
        """
        toneData is l6p json file content serialized
        To be tested
        """
        data = {"token": self.token, "upload": toneData}
        print(toneData)
        r = self.session.post(self.API_ENDPOINT + "customtone/tone", data=data)
        
        print(json.dumps(r.json(), indent=4, sort_keys=True))

    def getUpdates(self, device=""):
        """
        Get device update information
        """
        d_id = self.getDeviceId(device)
        r = self.getRequest("release/list?format=json&midi_id={0}".format(d_id))
        print(json.dumps(r.json(), indent=4, sort_keys=True))

    def setFavouriteTone(self, tone_id, song_id):
        """
        Set tone as favourite for a song_id.
        A favourite must be linked to a song.
        There can only be one favourite for a song_id.
        (See how this could be hacked to use song_id as a system of favourite slots)
        """
        try:
            r = self.getRequest("customtone/favorite?format=json&id={0}&songs_id={1}".format(tone_id, song_id))
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        except:
            print("Connection error")
            
    def getDeviceId(self, device):
        """
        Return device id as defined by line6
        """
        if device in self.midi_id:
            return self.midi_id[device]
        else:
            return ""
        
    def getRequest(self, req):
        """
        Api get request
        """
        creq = self.API_ENDPOINT + req + "&token={0}&appname=AMPLIFi Remote&appver=2.61.0".format(self.token)
        #print(creq)
        return self.session.get(creq)
    


    def orderByDownload(self, tone):
        """
        Utility function to order list of tone in function of the download count.
        """
        try:
            return tone.getDownloadCount()
        except KeyError:
            return 0
