# %%
import json

import csv

import tweepy

import re

import yweather

import pandas as pd

import pytest as pytest

# %%
#Twitter API credentials

consumer_key = ""

consumer_secret = ""

access_key = ""

access_secret = ""



#authorize twitter, initialize tweepy

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)

# %%
import os

from google.cloud import language_v1



credential_path = "D:\Download\ec601-327201-544fe77b03a7.json"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# Instantiates a client

client = language_v1.LanguageServiceClient()



def sentimentScore(text):

    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text

    sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment

    return sentiment.score

def test_sentimentScore():
    assert sentimentScore("") == 0
    assert sentimentScore("a") != 0
    assert sentimentScore("good") > 0
    assert sentimentScore("bad") < 0

# %%
def getCorodinate(place):

    from geopy.geocoders import Nominatim

    geolocator = Nominatim(user_agent="myapp")

    location = geolocator.geocode(place)

    return location.latitude, location.longitude

def test_getCorodinate():
    from pytest import approx
    with pytest.raises(AttributeError):
         getCorodinate("esadg") 
    
    with pytest.raises(AttributeError):
        getCorodinate("!@#$")

    assert approx(getCorodinate("chaoyang,beijing"), rel=1e-1) == getCorodinate("朝阳，北京")

# %%
def getWOEID(place):

    try:

        trends = api.trends_available()

        for val in trends:

            if (val['name'].lower() == place.lower()):

                return(val['woeid']) 

        print('Location Not Found')

    except Exception as e:

        print('Exception:',e)

        return(0)

def test_getWOEID():
    assert getWOEID("!@#") == None
    assert getWOEID("123") == None
    assert getWOEID("YYY") == None
    assert type(getWOEID("boston")) == int

# %%
def get_trends_by_location(loc_id,count=50):

    try:

        trends = api.trends_place(loc_id)

        df = pd.DataFrame([trending['name'],  trending['tweet_volume'], trending['url']] for trending in trends[0]['trends'])

        df.columns = ['Trends','Volume','url']

        # df = df.sort_values('Volume', ascending = False)

        # print(df[:count])

        return(df['Trends'][:count])

    except Exception as e:

        print("An exception occurred",e)

    

print(get_trends_by_location(getWOEID('boston'),10))

def test_get_trends_by_location():
        get_trends_by_location(getWOEID('boston'),10).shape == (10,3)
# %%
def search_for_phrase(phrase,place,amount):

    try:

        df = pd.DataFrame( columns = ["text",'sentiment score'])

        latitude = getCorodinate(place)[0]

        longitude = getCorodinate(place)[1]

        for tweet in tweepy.Cursor(api.search, q=phrase.encode('utf-8') +' -filter:retweets'.encode('utf-8'),geocode=str(latitude)+","+str(longitude)+",100km",lang='en',result_type='recent',tweet_mode='extended').items(amount):

            txt = tweet.full_text.replace('\n',' ').encode('utf-8')

            df=df.append({"text": txt,'sentiment score': sentimentScore(txt)},ignore_index=True)

        # print (df)

        return phrase, df['sentiment score'].mean(), df['sentiment score'].var()

        

    except Exception as e:

        print("An exception occurred",e)



search_for_phrase('pizza','boston',10)

# %%
def getResult(place):

    data=[]

    trends = get_trends_by_location(getWOEID(place),10)

    for phrase in trends:

        data.append(search_for_phrase(phrase,place,10))

    df = pd.DataFrame(data,columns=['trends','mean of sentiment-score','variance of sentiment-score'])

    print (df)

# %%
if __name__ == '__main__':

    getResult("boston")
