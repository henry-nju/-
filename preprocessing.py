import re
import jieba

data_path       = '../1_数据获取/data/'          # 存放预处理后新闻数据的目录
wordtable_path  = './wordtable.txt'             # 词表路径
stopwords_path  = './stopwords/中文停用词表.txt'  # 停止词表路径

with open(stopwords_path) as f:
    stopwords = f.readlines()
stopwords = set(map(lambda x:x.strip(), stopwords))  # 去除末尾换行符
len(stopwords)

jieba.load_userdict('user_dict.txt')  # 用户词典
word_table = {}  # 词表

for i in range(1, 1003):
    # 读取新闻文本
    with open(data_path + str(i) + '.txt') as f:
        content = f.read()

    # 全文统一处理
    content = content.replace('丨', ' ')  # 替换特殊字符
    content = content.replace(u'\t', '')  # 去除制表符
    content = content.replace(u'\xa0', '')  # 去除全角空格
    content = content.replace(u'\u3000', '')  # 去除不间断空白符

    # 分割为句子的列表
    content = re.split('，|。|；|？|！|：|\n', content)
    content = list(filter(None, content))  # 去除空句子

    print(i, len(content), 'sentences')

    # 逐句处理并写入
    file = open('./data/' + str(i) + '.txt', 'w')
    for sentence in content:
        sentence = sentence.strip()
        cop = re.compile("[^\u4e00-\u9fa5]")
        sentence = cop.sub(' ', sentence)  # 将无效字符替换为空格

        # 分词、去除停止词
        sentence = jieba.cut(sentence)  # 分词
        word_list = [word.strip() for word in sentence if word.strip() and word not in stopwords]  # 去除停止词
        sentence = ' '.join(word_list)  # 用空格分隔分词结果

        for word in word_list:
            word = word.strip()
            word_table[word] = word_table.get(word, 0) + 1  # 频数加一

        if sentence:
            file.write(sentence + '\n')  # 写文件
    file.close()