from os import listdir
import operator
from enum import Enum


class SortType(Enum):
    SORT_BY_ALPHABETICALLY = 0,
    SORT_BY_WORD_COUNT = 1,
    SORT_BY_WORD_COUNT_REVERSE = 2


class CountScoreTool:
    # 特殊字，用來檢查文字檔不應出現的字
    special_words = ['ㄧ']
    # 標點符號，用來檢查文字檔不應出現的標點符號
    full_punctuation = ' ，：!"#$%&\\()*+,-./:;<=>?@[\\]^_`{|}~→↓△▿⋄•！？。?〞＃＄％＆』（）＊＋－╱︰；＜＝＞＠〔╲〕 ＿ˋ｛∣｝∼、〃》「」『』【】﹝﹞【】〝〞–—『』「」…﹏'
    # 積分計算方式
    score = {
        '0': 5,
        '1~4': 2,
        '5~9': 1,
        '>10': 0
    }

    def __init__(self, word_dict_file, pron_compare_file,
                 sentence_base_dir, pron_count_file):
        # 原始字詞字典檔路徑
        self.word_dict_file = word_dict_file
        # 音節單元單字對照檔路徑
        self.pron_compare_file = pron_compare_file
        # 文字基底文字檔放置的資料夾路徑
        self.sentence_base_dir = sentence_base_dir
        # 音節單元count檔路徑
        self.pron_count_file = pron_count_file

    # 根據原始字詞字典檔來產出音節單元單字對照檔
    def produce_pron_compare_file(self, SORT_TYPE=None):
        # 依據檔案的格式，建立word_dict => key為音節，value為文字List(不重複)
        word_dict = {}
        with open(self.word_dict_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = list(filter(lambda t: True if t != '' else False, line.strip().split(',')))
                sentence = line[0]
                sentence_pron = line[1:]

                count = 0
                for pron in sentence_pron:
                    if pron in word_dict.keys():
                        word_dict[pron].add(sentence[count])
                    else:
                        word_dict[pron] = set(sentence[count])
                    count += 1

        # 選擇排序方式
        if SORT_TYPE == SortType.SORT_BY_ALPHABETICALLY:
            word_dict = dict(sorted(word_dict.items(), key=lambda x: x[0].lower()))

        # 寫出音節單元單字對照檔
        with open(self.pron_compare_file, 'w', encoding='utf-8') as f:
            count = 1
            for key, value_group in word_dict.items():
                f.write(str(count) + ',')
                f.write(key + ',')
                f.write(','.join(value_group))
                f.write('\n')
                count += 1

    # 檢查每個文字基底文字檔，是否有不當的標點符號(暫時不檢查這個)、不當中文字、英文字、數字
    # 並存放到correct_sentence_base_path, incorrect_sentence_base_path
    def check_sentence_base_file(self):
        # 從音節單字對照檔中取得所有不重複的中文字
        one_word_set = set()
        with open(self.pron_compare_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().split(',')[2:]
                one_word_set.update(line)
        files = listdir(self.sentence_base_dir)

        # 用來存放正確文字基底檔案的路徑
        correct_files_path = []
        # key用來存放錯誤文字基底檔案的路徑，value存放錯誤原因
        incorrect_files_path = {}
        for filename in files:
            # 取得文字基底文字檔路徑
            full_path = self.sentence_base_dir + '/' + filename
            with open(full_path, 'r', encoding='utf-8') as f:
                # 考慮有些文字基底檔案會有標點符號，因此取出每一句時
                # 忽略標點符號
                text_list = [i for i in f.read() if not (i in self.full_punctuation)]
                is_correct = True
                for text in text_list:
                    # 檢查文字是否是特殊中文字
                    if text in self.special_words:
                        incorrect_files_path[full_path] = '出現特殊字等錯誤'
                        is_correct = False
                        break
                    # 檢查文字是否是英文字
                    elif text.encode('utf-8').isalpha():
                        incorrect_files_path[full_path] = '出現英文字等錯誤'
                        is_correct = False
                        break
                    # 檢查文字是否在字典裡面
                    elif not (text in one_word_set):
                        incorrect_files_path[full_path] = '有字不在字典裡等錯誤'
                        is_correct = False
                        break
                # 代表此句子每一個文字皆正確，則加入正確檔案路徑裡
                if is_correct:
                    correct_files_path.append(full_path)
        self.incorrect_sentence_base_path = incorrect_files_path
        self.correct_sentence_base_path = correct_files_path

    def produce_pron_count_file(self, SORT_TYPE=None):
        # 讀取全部文字基底檔案並進行每一個字的count計算
        sentence_base_words_count = {}
        for file in self.correct_sentence_base_path:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    for word in line:
                        # 檢查是不是標點符號(因為前面檢查時，標點符號先忽略了)
                        if not (word in self.full_punctuation):
                            # 檢查word是否已經在dict裡面
                            if not (word in sentence_base_words_count):
                                sentence_base_words_count[word] = 0
                            else:
                                sentence_base_words_count[word] += 1

        # 讀取音節單元單字對照檔並對比文字基底檔案產生出來的文字出現次數
        pron_count_collection = []
        with open(self.pron_compare_file, 'r', encoding='utf-8') as f:
            for line in f:
                pron_count = []
                words_line = line.strip().split(',')[2:]
                # 判斷字典裡的字是不是出現在文字基底文字中，並且次數需要大於0，才算進去
                word_list = [word for word in words_line if word in sentence_base_words_count and sentence_base_words_count[word] > 0]
                # 加總同一音節單元的全部count次數
                sum_count = 0
                words_count = []
                for word in word_list:
                    count = sentence_base_words_count[word]
                    words_count.append([word + ':' + str(count)])
                    sum_count += count
                # 最後合併為一個list
                line = line.strip().split(',')[:2]
                line.append(str(sum_count))
                line.extend([text for word in words_count for text in word])
                pron_count.extend(line)
                pron_count_collection.append(pron_count)

        # 選擇排序方式
        if SORT_TYPE == SortType.SORT_BY_WORD_COUNT:
            pron_count_collection = sorted(pron_count_collection, key=lambda x: int(x[2]))
        elif SORT_TYPE == SortType.SORT_BY_WORD_COUNT_REVERSE:
            pron_count_collection = sorted(pron_count_collection, key=lambda x: int(x[2]), reverse=True)
        else:
            pron_count_collection = sorted(pron_count_collection, key=lambda x: x[1].lower())

        # 將音節單元count字典檔寫檔
        with open(self.pron_count_file, 'w', encoding='utf-8') as f:
            for line in pron_count_collection:
                f.write(','.join(line))
                f.write('\n')

    # 涵蓋率分析=>分析音節單元count字典檔中次數出現的比例
    def analysis_pron_count_file(self):
        analysis_dict = {
            '0次': 0,
            '1~4次': 0,
            '5~9次': 0,
            '>10次': 0
        }
        with open(self.pron_count_file, 'r', encoding='utf-8') as f:
            for line in f:
                count = int(line.strip().split(',')[2])
                if count == 0:
                    analysis_dict['0次'] += 1
                elif 1 <= count <= 4:
                    analysis_dict['1~4次'] += 1
                elif 5 <= count <= 9:
                    analysis_dict['5~9次'] += 1
                else:
                    analysis_dict['>10次'] += 1
            total_value = sum(analysis_dict.values())
            for key, value in analysis_dict.items():
                analysis_dict[key] = str(value) + '個' + '，' + str(round((value / total_value * 100), 2)) + '%'
        return analysis_dict

    # 計算單一句子的積分
    def calculate_sentence_score(self, sentence):
        pron_compare_dict = {}
        with open(self.pron_compare_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().split(',')
                pron = line[1]
                id_with_words = line[2:]
                id_with_words.insert(0, line[0])
                pron_compare_dict[pron] = id_with_words

        # 從音節單元count字典檔中取得每一個字的count數目並轉成dict
        id_count = {}
        with open(self.pron_count_file, 'r', encoding='utf-8') as f:
            for line in f:
                count = int(line.split(',')[2])
                id = line.strip().split(',')[0]
                id_count[id] = count

        # 從單一句子中取出每一個中文字，並比對是否文字在音節單元count字典檔中
        single_word_score = {}
        sum_score = 0
        not_exist = True
        not_exist_words = set()
        for word in sentence:
            for key, value in pron_compare_dict.items():
                if word in value:
                    id = pron_compare_dict[key][0]
                    count_num = id_count[id]
                    # 依據出現次數去做積分加總
                    if count_num == 0:
                        word_score = self.score['0']
                    elif 1 <= count_num <= 4:
                        word_score = self.score['1~4']
                    elif 5 <= count_num <= 9:
                        word_score = self.score['5~9']
                    else:
                        word_score = self.score['>10']
                    sum_score += word_score

                    # 判斷該中文字是否已經在每個字的分數集合裡面
                    if word in single_word_score:
                        single_word_score[word] += word_score
                    elif word_score > 0:
                        single_word_score[word] = word_score
                    not_exist = False
                    break

            if not_exist:
                not_exist_words.add(word)
                sum_score += 0
        average_score = round(sum_score / len(sentence), 2)
        single_word_score = sorted(single_word_score.items(), key=operator.itemgetter(1), reverse=True)

        # 如果為空，代表裡面的字的分數都 = 0分
        if single_word_score:
            info_msg = [str(average_score) + '分,',
                        str(len(sentence)) + '個字,',
                        ','.join(f'{pair[0]}:{pair[1]}' for pair in single_word_score) + ', ']
        else:
            info_msg = [str(average_score) + '分,',
                        str(len(sentence)) + '個字,']
        if not_exist_words:
            info_msg.append('錯誤:有字不在字典裡 => ' + str(','.join(not_exist_words)))
        else:
            info_msg.append('正確')
        return info_msg

    # 計算大量句子在文字檔的每個分數
    def calculate_sentences_score(self, source_filepath, dest_filepath, SORT_TYPE=None):
        with open(source_filepath, 'r', encoding='utf-8') as f:
            sentence_list = [line.strip() for line in f]

        message = []
        line_count = 1
        for sentence in sentence_list:
            info = [str(line_count), self.calculate_sentence_score(sentence)]
            message.append(info)
            line_count += 1

        if SORT_TYPE == SortType.SORT_BY_WORD_COUNT:
            message = sorted(message, key=lambda x:float(x[1][0][:x[1][0].index('分')]))
        elif SORT_TYPE == SortType.SORT_BY_WORD_COUNT_REVERSE:
            message = sorted(message, key=lambda x: float(x[1][0][:x[1][0].index('分')]), reverse=True)

        with open(dest_filepath, 'w', encoding='utf-8') as f:
            for info in message:
                f.write(info[0] + ',' + ''.join(info[1]) + '\n')