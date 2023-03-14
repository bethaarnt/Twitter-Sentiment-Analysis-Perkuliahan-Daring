import time
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
seed = 0
np.random.seed(seed)
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = 'whitegrid')
import re
import string
import json
from PIL import Image
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from keras.preprocessing.text import Tokenizer, tokenizer_from_json
from keras.utils import pad_sequences
from keras.models import Model, load_model

st.write("""
# Analisis Sentimen Perkuliahan daring Menggunakan LSTM 📚

# """)

# load dataset
tweets_data = pd.read_csv('dataset_clean_sentiment.csv')

# Preprocessing
def cleaningText(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text) 
    text = re.sub(r'#[A-Za-z0-9]+', '', text) 
    text = re.sub(r'RT[\s]', '', text) 
    text = re.sub(r"http\S+", '', text)
    text = re.sub(r'[0-9]+', '', text)

    text = text.replace('\n', ' ')
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.strip(' ')
    return text

def casefoldingText(text): 
    text = text.lower() 
    return text

def tokenizingText(text):
    text = word_tokenize(text) 
    return text

def filteringText(text): 
    listStopwords = set(stopwords.words('indonesian'))
    filtered = []
    for txt in text:
        if txt not in listStopwords:
            filtered.append(txt)
    text = filtered 
    return text

def stemmingText(text): 
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    text = [stemmer.stem(word) for word in text]
    return text

def toSentence(list_words):
    sentence = ' '.join(word for word in list_words)
    return sentence

# Tokenizer
X = tweets_data['tweet']
max_features = 5000

with open('tokenizer.json') as f:
    data = json.load(f)
    tokenizer = tokenizer_from_json(data)

X = tokenizer.texts_to_sequences(X.values)
X = pad_sequences(X)
X.shape

# Encode target data into numerical values
sentiment_encode = {'negative' : 0, 'neutral' : 1, 'positive' : 2}
y = tweets_data['sentiment'].map(sentiment_encode).values

# select
select = st.selectbox('Pilih Skenario ', ['Explore Visualisasi Data','Skenario Baseline', 'Skenario Modifikasi'], key=1)
polarity = tweets_data['sentiment'].value_counts()
polarity = pd.DataFrame({'polarity': polarity.index, 'Tweets': polarity.values})

def modelPrediction(text):
    if(select == 'Skenario Baseline'):
        model = load_model('model_baseline.h5')
    else:
        model = load_model('model_modifikasi.h5')
        
    if st.button('Hasil Predict Sentiment 👈'):
        text = [input_text]
        new_text = []
        for text in text:
            preprocessed_text = toSentence(stemmingText(filteringText(tokenizingText
                                (casefoldingText(cleaningText(text))))))
            new_text.append(preprocessed_text)

        text_seq = tokenizer.texts_to_sequences(new_text)
        textPadded_seq = pad_sequences(text_seq, maxlen = 47)
        text_pred = model.predict(textPadded_seq)
        text_pred = np.argmax(text_pred)

        if text_pred == 0:
            text_result = st.error('Negatif')
        elif text_pred == 1:
            text_result = st.warning('Neutral')
        else:
            text_result = st.success('Positive')
        print(text_result)
    
# choose explore
if select == 'Explore Visualisasi Data':
    st.header('Visualisasi Dataset✨')
    if st.checkbox('Show Dataset'):
        st.write(tweets_data)
    
    fig = px.pie(polarity, values='Tweets', names='polarity', color='polarity', width=600)
    st.plotly_chart(fig)
    st.write('Diperoleh data dengan label negative ada 51,1% (12778 data), positive ada 33,5% (8366 data) dan netral ada 15,4% (3856 data).')
    fig = px.bar(polarity, x='polarity', y='Tweets', color='Tweets', height=500, width=500)
    st.plotly_chart(fig)

    st.header('Positive and Negative Word Cloud')
    st.image('img/wordcloud.png')
    st.write('WordCloud di atas merupakan representasi visual dari kumpulan kata-kata positive dan negative yang disusun secara acak dalam ukuran dan bentuk yang berbeda, di mana kata-kata yang paling sering muncul akan lebih besar dan lebih menonjol daripada kata-kata yang jarang muncul.')
    
# choose baseline
elif select == 'Skenario Baseline':
    st.header("Model LSTM pada Percobaan Baseline")
    st.header('Prediction with custom text ')
    input_text = st.text_area('Masukkan Teks :')
    text_result = ''
    modelPrediction(input_text)
    
    st.subheader('Hyperparameter yang digunakan :')
    df = pd.DataFrame({
        'Hyperparameter': ['batch_size', 'dropout_rate','embedding_size', 'optimizer', 'learning_rate', 'activation', 'hidden_unit', 'epoch'],
        'Value': [128, 0.2, 32, 'RMSprop', 0.001, 'tanh', 16, 10],
    })
    st.table(df)
    
    st.header('Grafik Akurasi 📈 ')
    st.image('img/acc_baseline.png')
    st.write('Hasil akurasi pada percobaan Baseline diperoleh sebesar 89,86%')
    st.header('Confusion Matrix: ')
    st.image('img/cf_baseline.png')
    st.write('Dari gambar confusion matrix diatas, diketahui bahwa model dapat memprediksi 2377 sentimen negatif, 607 sentimen netral dan 1509 sentimen positif dengan benar.')

# choose modifikasi
else:
    st.header("Model LSTM Modifikasi")
    st.header('Prediction with custom text ')
    input_text = st.text_area('Masukkan Teks :')
    text_result = ''
    modelPrediction(input_text)
    st.subheader('Hyperparameter yang digunakan :')
    df = pd.DataFrame({
        'Hyperparameter': ['batch_size', 'dropout_rate','embedding_size', 'optimizer', 'learning_rate', 'activation', 'hidden_unit', 'epoch'],
        'Value': [64, 0.1, 32, 'RMSprop', 0.001, 'tanh', 16, 8],
    })
    st.table(df)
    
    st.header('Grafik Akurasi 📈 ')
    st.image('img/acc_modifikasi.png')
    st.write('Hasil akurasi pada percobaan Modifikasi diperoleh sebesar 90,02%')
    st.header('Confusion Matrix: ')
    st.image('img/cf_modifikasi.png')
    st.write('Dari gambar confusion matrix diatas, diketahui bahwa model dapat memprediksi 2397 sentimen negatif, 593 sentimen netral dan 1511 sentimen positif dengan benar.')
    
    

