import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()
from stop_words import get_stop_words
import re
from wordcloud import WordCloud
from datetime import datetime


def clean_text(text):
    #remove \n=
    text = text.replace('\n',' ')
    
    #Remove punctuations
    text = re.sub(r'[?!.;:,#@-]', '', text)

    #Convert to lowercase to maintain consistency
    text = text.lower()
    return text

def gen_freq(text,nb_words=20):
    #Will store the list of words
    word_list = []

    #Loop over all the tweets and extract words into word_list
    for tw_words in text.split():
        word_list.append(tw_words)

    #Create word frequencies using word_list
    stopwords = get_stop_words('fr',cache=False)
    word_freq = pd.Series(word_list).value_counts()
    word_freq = word_freq.drop(labels=stopwords, errors='ignore')
    
    word_freq[:nb_words]
    
    return word_freq

def all_lyrics():
    s=''
    for i in range(len(songs['lyrics'])):
        s = s.__add__(songs.loc[i,'cleaned_lyrics'])

    return s

def artist_lyrics(artist):
    s = ''
    for i in range(len(songs['lyrics'])):
        if songs.loc[i,'artist'] == artist:
          s += songs.loc[i,'cleaned_lyrics']
    return s

def lexdiv(lyrics):
    try:
        return len(set(lyrics.split()))/float(len(lyrics.split()))
    except:
        return 0

def calcFreqOfTerm(artist, terms):    
    # Determine how many songs mention a given term
    sgs = songs[songs['artist'] == artist]
    sgs.reset_index(drop=True,inplace=True)
    song_count, term_count = len(sgs), 0
    for i in range(len(sgs)):
        for term in terms:            
            if term.lower() in sgs.loc[i,'cleaned_lyrics'].lower():
                term_count += 1
                break

    term_freq = round(term_count/float(song_count),5)    
    data = np.reshape([term_freq, term_count, song_count],(1,3))
    # return data
    return pd.DataFrame(data, columns=['frequency','count','total'], index=[artist])

def calcTermFreqAcrossArtists(artists, terms):
    if not isinstance(terms, list):
        terms = [terms]

    term_freqs = pd.concat([calcFreqOfTerm(artist, terms) for artist in artists],axis=0)
    term_freqs.term = "_OR_".join(terms)
    return term_freqs


def fitLine(x, y):
    A = np.vstack([x, np.ones(len(x))]).T
    soln = np.linalg.lstsq(A, y, rcond=None)[0]    
    
    # residual sum of squares
    y_fit = soln[0]*x + soln[1]
    ss_res = np.sum((y - y_fit)**2) # residuals ?
    ss_tot = np.sum((y - y.mean())**2) # total sum of squares
    r2 = round(1 - (ss_res / ss_tot), 3) # r-squared
        
    return y_fit, x, r2

songs = pd.read_csv('data/songs.csv')
songs = songs.drop(['Unnamed: 0','fact_track','song_story'],axis=1)
songs.dropna(inplace=True)

artists = np.unique(songs['artist'])

songs['release_date'] = [datetime.strptime(x,'%Y-%m-%d') for x in songs['release_date']]

songs['age'] = [ (datetime.now() - x).days/365.25 for x in songs['release_date']]
songs = songs[songs['age'] < 35]

songs['cleaned_lyrics']= [clean_text(item) for item in songs['lyrics']]

songs['lexical_diversity'] = songs['cleaned_lyrics'].apply(lexdiv)
lexical_diversity = songs.groupby('artist')['lexical_diversity'].describe()
min_lexdiv = artists[lexical_diversity['mean'].argmin()]
max_lexdiv = artists[lexical_diversity['mean'].argmax()]

songs.reset_index(drop=True,inplace=True)