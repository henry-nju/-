import os
import jieba
from collections import Counter
import re

n = 3  # 3-gram

data_path       = './2_预处理/data/'          # 存放预处理后新闻数据的目录
wordtable_path  = './2_预处理/wordtable.txt'  # 词表路径
stopwords_path  = './2_预处理/stopwords/中文停用词表.txt' # 停止词表路径
testset_path    = './testset/'
prediction_path = './predictions/'

ngrams_list = []  # n元组（分子）
prefix_list = []  # n-1元组（分母）

# 遍历所有预处理过的新闻文件
for i, datafile in enumerate(os.listdir(data_path)):
    with open(data_path + datafile, encoding='utf-8') as f:
        for line in f:
            sentence = ['<BOS>'] + line.split() + ['<EOS>']
            ngrams = list(zip(*[sentence[i:] for i in range(n)]))   # 一个句子中n-gram元组的列表
            prefix = list(zip(*[sentence[i:] for i in range(n-1)])) # 历史前缀元组的列表
            ngrams_list += ngrams
            prefix_list += prefix

ngrams_counter = Counter(ngrams_list)
prefix_counter = Counter(prefix_list)

all_words = []  # 词表中的全部
with open(wordtable_path, encoding='utf-8') as f:
    for line in f.readlines()[1:]:
        all_words.append(line.split()[-1])

# 停止词
with open(stopwords_path) as f:
    stopwords = f.readlines()
stopwords = set(map(lambda x:x.strip(), stopwords))  # 去除末尾换行符


def probability(sentence):
    prob = 1  # 初始化句子概率
    ngrams = list(zip(*[sentence[i:] for i in range(n)]))
    for ngram in ngrams:
        prob *= (1 + ngrams_counter[ngram]) / (len(prefix_counter) + prefix_counter[(ngram[0], ngram[1])])
    return prob


def predict(pre_sentence, post_sentence, all_words, cand_num=1):
    word_prob = []
    for word in all_words:
        test_sentence = pre_sentence[-(n-1):] + [word] + post_sentence[:(n-1)]
        word_prob.append( (word, probability(test_sentence)) )

    return sorted(word_prob, key=lambda tup: tup[1], reverse=True)[:cand_num]


# 加载测试集标签（答案）
with open('testset/answer.txt', encoding='utf-8') as f:
    answers = [answer.strip() for answer in f]  # 答案构成的列表

prediction_file = open(prediction_path + 'prediction_ngram.txt', 'w', encoding='utf-8')  # 存放预测结果

# 开始测试
correct_count = 0

with open('testset/questions.txt', encoding='utf-8') as f:
    questions = f.readlines()
    total_count = len(questions)
    for i, question in enumerate(questions):
        question = question.strip()
        pre_mask = question[:question.index('[MASK]')]
        post_mask = question[question.index('[MASK]') + 6:]

        pre_sentence = jieba.cut(pre_mask.replace('，', ' '))
        post_sentence = jieba.cut(post_mask.replace('，', ' '))
        pre_sentence = [word.strip() for word in pre_sentence if word.strip() and word not in stopwords]
        post_sentence = [word.strip() for word in post_sentence if word.strip() and word not in stopwords]

        predict_cand = predict(pre_sentence, post_sentence, all_words)
        prediction_file.write(' '.join([w[0] for w in predict_cand]) + '\n')

        for j, p in enumerate(predict_cand):
            if p[0] == answers[i]:
                print(i, '{} [{}] {}'.format(pre_mask, p[0], post_mask))
                correct_count += 1
                break

prediction_file.close()

print('准确率：{}/{}'.format(correct_count, total_count))