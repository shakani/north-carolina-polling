import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }


df = pd.DataFrame([], columns=['countyID', 'pollingID', 'County','Precinct','Polling Location','Address1','Address2','Zip Code'])

def firstWord(st):
    a = st.split(' ')
    return a[0]

def cleanText(arr):
    return ''.join([c for c in arr if c not in '\r\t\n'])

def getRow(countyID, pollingID):
    url = 'https://vt.ncsbe.gov/PPLkup/PollingPlaceResult/?CountyID={}&PollingPlaceID={}'.format(countyID, pollingID)

    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    checker = soup.find_all('div', id='resultsNotFound')

    if bool(len(checker)):
        return False
    else: 
        a = [link.text for link in soup.find_all('a')]
        a = list(filter(lambda s: 'County' in s, a))

        myCounty = firstWord(cleanText(a[0])) # works

        d = soup.find_all('div', id='divPollingPlace')
        pollingInfo = [p.text for p in d]
        pollingInfo = [''.join([c for c in p if c not in '\r\t']) for p in pollingInfo]
        pollingInfo = pollingInfo[0]
        pollingInfo = pollingInfo.split('\n')
        pollingInfo = [s for s in pollingInfo if s != '']

        myPollingLocation, address1, address2, myPrecinct = pollingInfo[0], pollingInfo[1], pollingInfo[2], pollingInfo[4]

        address2 = address2.split(' ')
        address2, zipCode = ' '.join(address2[:-1]), address2[-1]

        return pd.Series([countyID, pollingID, myCounty, myPrecinct, myPollingLocation, address1, address2, zipCode], index=df.columns)

def csvAppend(cMax, pMax, cStart=1, pStart=1):
    for countyID in range(cStart, cMax+1):
        print(countyID)
        for pollingID in range(pStart, pMax+1):
            line = getRow(countyID, pollingID)
            if type(line) != type(False):
                myLine = pd.DataFrame(line).T
                myLine.to_csv('nc-polling-data.csv',mode='a', header=False)

csvAppend(100,250)
print('Done')
