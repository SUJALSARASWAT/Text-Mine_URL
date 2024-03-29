# -*- coding: utf-8 -*-
"""Untitled14.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19tP0NcCM_6neeWhCzT-DzR5fxKS9Ys7d
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import nltk

nltk.download('punkt')

def extract_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('title').get_text()
    article_text = ' '.join([p.get_text() for p in soup.find_all('p')])

    return title, article_text

def clean_text(text, stop_words):
    cleaned_text = re.sub(r'\s+', ' ', re.sub('[^A-Za-z0-9\s]+', '', text))
    cleaned_text = ' '.join([word for word in cleaned_text.split() if word.lower() not in stop_words])
    return cleaned_text

def text_analysis(cleaned_text, positive_words, negative_words):
    sentences = sent_tokenize(cleaned_text)
    words = word_tokenize(cleaned_text)

    cleaned_words = [word for word in words]

    positive_score = sum(1 for word in cleaned_words if word.lower() in positive_words)
    negative_score = sum(1 for word in cleaned_words if word.lower() in negative_words)

    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(cleaned_words) + 0.000001)

    avg_sentence_length = len(words) / len(sentences)
    complex_words = [word for word in cleaned_words if len(word) > 2]
    percentage_complex_words = len(complex_words) / len(cleaned_words)
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    avg_words_per_sentence = len(cleaned_words) / len(sentences)

    complex_word_count = len(complex_words)

    cleaned_word_count = len(cleaned_words)

    syllables = sum(len(re.findall(r'[aeiouy]+', word.lower())) for word in cleaned_words)

    personal_pronouns = sum(1 for word in cleaned_words if word.lower() in ["i", "we", "my", "ours", "us"])

    avg_word_length = sum(len(word) for word in cleaned_words) / len(cleaned_words)

    return {
        'POSITIVE SCORE': positive_score,
        'NEGATIVE SCORE': negative_score,
        'POLARITY SCORE': polarity_score,
        'SUBJECTIVITY SCORE': subjectivity_score,
        'AVG SENTENCE LENGTH': avg_sentence_length,
        'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words,
        'FOG INDEX': fog_index,
        'AVG NUMBER OF WORDS PER SENTENCE': avg_words_per_sentence,
        'COMPLEX WORD COUNT': complex_word_count,
        'WORD COUNT': cleaned_word_count,
        'SYLLABLE PER WORD': syllables / len(cleaned_words),
        'PERSONAL PRONOUNS': personal_pronouns,
        'AVG WORD LENGTH': avg_word_length
    }

index_data = pd.read_excel('Input.xlsx')

stop_words_files = ['StopWords_GenericLong.txt', 'StopWords_Geographic.txt', 'StopWords_Currencies.txt',
                    'StopWords_DatesandNumbers.txt', 'StopWords_Generic.txt', 'StopWords_Auditor.txt',
                    'StopWords_Names.txt']

stop_words = set()
for file_path in stop_words_files:
    try:
        new_stop_words = pd.read_csv(file_path, header=None, encoding='latin1', sep='|').iloc[:, 0].apply(lambda x: str(x).lower()).tolist()
        stop_words.update(new_stop_words)
    except pd.errors.ParserError as e:
        print(f"Error reading file {file_path}: {e}")


positive_words = set(pd.read_csv('positive-words.txt', header=None, encoding='latin1', squeeze=True).str.lower())
negative_words = set(pd.read_csv('negative-words.txt', header=None, encoding='latin1', squeeze=True).str.lower())

output_data = pd.DataFrame()

for index, row in index_data.iterrows():
    url_id = row['URL_ID']
    url = row['URL']

    title, article_text = extract_text(url)

    cleaned_text = clean_text(article_text, stop_words)

    with open(f'{url_id}.txt', 'w', encoding='utf-8') as file:
        file.write(f'{title}\n\n{cleaned_text}')

    try:
        analysis_results = text_analysis(cleaned_text, positive_words, negative_words)
    except Exception as e:
        print(f"Error analyzing text for URL_ID {url_id}: {e}")
        continue


    analysis_results_df = pd.DataFrame([analysis_results])
    analysis_results_df['URL_ID'] = url_id
    analysis_results_df['URL'] = url
    output_data = pd.concat([output_data, analysis_results_df], ignore_index=True)


output_data.to_excel('Output Data Structure.xlsx', index=False)

