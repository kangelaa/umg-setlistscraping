import requests, calendar
from datetime import datetime, date
from bs4 import BeautifulSoup as bs4
import numpy as np, pandas as pd

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

while not beforeDate:
    showurl = f'https://www.setlist.fm/setlists/taylor-swift-3bd6bc5c.html?page={i}'
    showdata = requests.get(showurl, headers=header)
    showsoup = bs4(showdata.text, 'html.parser')
    events = showsoup.findAll('div', class_='col-xs-12 setlistPreview vevent')
    for event in events:
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

showsdf = pd.concat([pd.DataFrame(showdates),pd.DataFrame(showcities),pd.DataFrame(showstates),pd.DataFrame(setlisturls)],axis=1)
showsdf.columns = ['Date', 'City', 'State/Country', 'setlistURL']
showsdf.dropna(inplace=True)
showsdf.reset_index(inplace=True,drop=True)
print(showsdf)

finalsongs = pd.DataFrame()

for i in range(len(showsdf)):

    #empty lists to store show data
    numsongs = 0
    setlistsongs = []

    setlisturl = showsdf.iloc[i,3]
    setlistdata = requests.get(setlisturl, headers = header)
    setlistsoup = bs4(setlistdata.text, 'html.parser')
    songs = setlistsoup.findAll('li', class_ = 'setlistParts song')
    numsongs = len(songs)

    for song in songs:
      setlistsongs.append(song.find('a', class_ = 'songLabel').string.lower())
    setlistdf = pd.DataFrame(setlistsongs,columns=['songName'])

    setlistdf['Date'] = showsdf.iloc[i,0]
    setlistdf['City'] = showsdf.iloc[i,1]
    setlistdf['State/Country'] = showsdf.iloc[i,2]
    finalsongs = pd.concat([finalsongs,setlistdf])

print(finalsongs)

#
# datetag = setlistsoup.find('div', class_ = 'dateBlock') # TODO: EDIT DATE AND LOCATIN COLUMNS BC YOU GOT MORE EFFICIENTLY ABOVE
# datestr = datetag.find('span', class_ = 'month').string + datetag.find('span', class_ = 'day').string + datetag.find('span', class_ = 'year').string
# date = datetime.strptime(datestr, '%b%d%Y').date().strftime('%Y-%m-%d')
# setlistdf['date'] = date
#
# #assumes that all the setlist websites across artists are set up like this
# location = setlistsoup.find('div', class_ = 'setlistHeadline').find(lambda tag:tag.name=='span' and "at " in tag.text).find('a').find('span').string
# setlistdf['city'] = location.split(', ')[1]
# setlistdf['state'] = location.split(', ')[2]
# print(setlistdf)

#
# pages = [5,2,2,3]
# cat = ['vinyl', 'box-sets', 'color-vinyl', 'cd']
# capture = {}
# for c, p in zip(cat,pages):
#
#   for i in range(1,p):
#   #  url = f'https://shop.udiscovermusic.com/collections/survey20?page={i}'
#
#     url = f'https://shop.urbanlegends.com/collections/{c}?page={i}'
#     #url = f'https://shop.urbanlegends.com/collections/vinyl?&page={i}'
#     agents = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
#     header = {
#           'User-Agent': agents,
#           'Accept-Language': 'en-US, en;q=0.5'
#       }
#     data = []
#     j = 0
#     response = requests.get(url, headers=header)
#     soups = bs(response.text, 'html.parser')
#     checks = soups.find_all('div', class_=(f"grid__item large--one-quarter medium--one-half"))
#     for check in checks:
#       data.append(check.find('h1').text)
#       data.append(check.find('h2').text)
#       xx = str(check)
#       xx = xx.split()
#       for x in xx:
#         if "data-variant-sku" in x:
#           data.append((x[16:33]))
#       name = f'{c}?page={i}_title{j}'
#       try:
#           for item in check.find('div', class_ = "product-availability"):
#             data.append(item)
#       except KeyError:
#           data.append('in stock')
#       if len(data) == 3:
#         data.append("in_stock")
#       capture[name] = data
#       j += 1
#       data = []
#     print(f'you have finished page {i}')