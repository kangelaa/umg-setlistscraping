import requests
from datetime import date
from bs4 import BeautifulSoup as bs4
import pandas as pd

agents = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
header = {
    'User-Agent': agents,
    'Accept-Language': 'en-US, en;q=0.5'
}

#only get songs for shows on or after this date
compdate = '2020-01-01'
todaysdate = str(date.today())

i = 1
beforeDate = False
showdates = []
showcities = []
showstates = [] #or countries if > US
setlisturls = []

#collect all show data between todays date and the comparison date
while not beforeDate:
    showurl = f'https://www.setlist.fm/setlists/taylor-swift-3bd6bc5c.html?page={i}' #need to configure to automate for each artist w/ MBID
    showdata = requests.get(showurl, headers=header)
    showsoup = bs4(showdata.text, 'html.parser')
    events = showsoup.findAll('div', class_='col-xs-12 setlistPreview vevent')
    for event in events:
        #first get and compare show date
        showdatetag = event.find('span', class_ = 'value-title')
        if showdatetag is not None:
            showdate = showdatetag.get('title')
        else:
            showdate = None
        if showdate < compdate:
            beforeDate = True
            break # TODO: MAKE SURE TO BREAK OUT OF ALL LOOPS
        elif showdate >= todaysdate:
            continue # dont get data for future shows
        else:
            #then collect other data and append to lists
            showdates.append(showdate)
            showcitytag = event.find('span', class_='locality')
            if showcitytag is not None:
                showcities.append(showcitytag.string)
            else:
                showcities.append(showcitytag)
            showstatetag = event.find('span', class_ = 'region')
            if showstatetag is not None:
                showstates.append(showstatetag.string)
            else:
                showcountrytag = event.find('span', class_='country-name')
                if showcountrytag is not None:
                    showstates.append(showcountrytag.string)
                else:
                    showstates.append(showstatetag)
            setlisturltag = event.find('a', class_ = 'summary url')
            if setlisturltag is not None:
                setlisturl = setlisturltag.get('href').replace('..', 'https://www.setlist.fm')
                setlisturls.append(setlisturl)
            else:
                setlisturls.append(setlisturltag)
    print(f'you have finished page {i}') #prints extra page at end after breaking, program ends on that page
    i += 1

#create df with all tour/shows data for particular artist
showsdf = pd.concat([pd.DataFrame(showdates),pd.DataFrame(showcities),pd.DataFrame(showstates),pd.DataFrame(setlisturls)],axis=1)
showsdf.columns = ['Date', 'City', 'State/Country', 'setlistURL']
showsdf.dropna(inplace=True)
showsdf.reset_index(inplace=True,drop=True)
print(showsdf)

finalsongs = pd.DataFrame()

for i in range(len(showsdf)): #iterate through each show

    #empty lists to store show data
    numsongs = 0
    setlistsongs = []

    setlisturl = showsdf.iloc[i,3]
    setlistdata = requests.get(setlisturl, headers = header)
    setlistsoup = bs4(setlistdata.text, 'html.parser')
    songs = setlistsoup.findAll('li', class_ = 'setlistParts song')
    numsongs = len(songs)

    #get all songs for particular show
    for song in songs:
      setlistsongs.append(song.find('a', class_ = 'songLabel').string.lower())
    setlistdf = pd.DataFrame(setlistsongs,columns=['songName'])

    #create df for one show, append to full df of all songs for all shows
    setlistdf['Date'] = showsdf.iloc[i,0]
    setlistdf['City'] = showsdf.iloc[i,1]
    setlistdf['State/Country'] = showsdf.iloc[i,2]
    finalsongs = pd.concat([finalsongs,setlistdf])

print(finalsongs)
finalsongs.to_csv('finalsongs.csv')
