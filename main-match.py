import math
import string
from nltk.corpus import stopwords
from collections import Counter
from nltk.stem.porter import *
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba


def tfidf_calc(text, corpus, k, file_path):
    # corpus = ['This is the first document.',
    #           'This is the second second document.',
    #           'And the third one.',
    #           'Is this the first document?', ]
    tv = TfidfVectorizer(use_idf=True, smooth_idf=True, norm=None)
    tv_fit = tv.fit_transform(corpus)
    new_corpus = tv.get_feature_names()[-1::-1]
    print(new_corpus)
    with open(file_path, 'w', encoding='utf_8') as f:
        for i in range(k):
            undetermined_words = synonym_replace(new_corpus[i])
            if len(undetermined_words) == 0:
                continue
            for j in range(len(undetermined_words)):
                f.write(text.replace(
                    new_corpus[i], undetermined_words[j]) + '\n')


def divide_text(text):
    seg_text = jieba.cut(text, cut_all=False)
    return ' '.join(seg_text)


def synonym_replace(word):
    with open('synonym.txt', 'r', encoding='utf_8') as f:
        synonym_database = list(
            map(lambda x: x.strip().split()[1:], f.readlines()))
    words = []
    flag = False
    for i in range(len(synonym_database)):
        for j in range(len(synonym_database[i])):
            if synonym_database[i][j] == word:
                for k in range(len(synonym_database[i])):
                    if synonym_database[i][k] == word:
                        continue
                    words.append(synonym_database[i][k])
                    flag = True
                    break
            if flag:
                break
        if flag:
            break
    return words


if __name__ == '__main__':
    with open('query.txt', 'r', encoding='utf_8') as f:
        text = f.readlines()
    corpus = list(map(divide_text, text))
    tfidf_calc(text[0], corpus, 3, 'new_query.txt')
