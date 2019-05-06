from count import CountScoreTool, SortType
import sys
from count_score_tool import Ui_MainWindow, QtGui
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QPushButton, QMainWindow


class AppWindow(QMainWindow):
    tool = None

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pb_word_dict_file.clicked.connect(self.word_dict_file_click)
        self.ui.pb_pron_compare_file.clicked.connect(self.pron_compare_file_click)
        self.ui.pb_sentence_base_dir.clicked.connect(self.sentence_base_file_dir_click)
        self.ui.pb_pron_count_file.clicked.connect(self.pron_count_file_click)
        self.ui.pb_produce_pron_count_file.clicked.connect(self.produce_pron_file_click)
        self.ui.pb_analysis_pron_count_file.clicked.connect(self.analysis_pron_count_file_click)
        self.ui.pb_sentences_file.clicked.connect(self.calculate_sentences_file_click)
        self.ui.pb_sentence.clicked.connect(self.calculate_sentence_click)
        self.ui.le_sentence.returnPressed.connect(self.calculate_sentence_click)

    def word_dict_file_click(self):
        filepath, filetype = QFileDialog. \
            getOpenFileName(self,
                            "選取文件",
                            "./",
                            "Text Files (*.txt)")
        self.ui.le_word_dict_file.setText(filepath)

    def pron_compare_file_click(self):
        filepath, filetype = QFileDialog. \
            getSaveFileName(self,
                            "選取文件",
                            "./",
                            "Text Files (*.txt)")
        self.ui.le_pron_compare_file.setText(filepath)

    def sentence_base_file_dir_click(self):
        dir = QFileDialog.getExistingDirectory(self,
                                               '選取資料夾',
                                               './')
        self.ui.le_sentence_base_dir.setText(dir)

    def pron_count_file_click(self):
        filepath, filetype = QFileDialog. \
            getSaveFileName(self,
                            "選取文件",
                            "./",
                            "Text Files (*.txt)")
        self.ui.le_pron_count_file.setText(filepath)

    def produce_pron_file_click(self):
        word_dict_file = self.ui.le_word_dict_file.text()
        pron_compare_file = self.ui.le_pron_compare_file.text()
        sentence_base_dir = self.ui.le_sentence_base_dir.text()
        pron_count_file = self.ui.le_pron_count_file.text()
        self.tool = CountScoreTool(word_dict_file, pron_compare_file,
                                   sentence_base_dir, pron_count_file)

        msgBox = QMessageBox()
        msgBox.setText('要如何排序?')
        msgBox.addButton(QPushButton('count排序由小到大'), QMessageBox.YesRole)
        msgBox.addButton(QPushButton('count排序由大到小'), QMessageBox.NoRole)
        msgBox.addButton(QPushButton('依照拼音字母排序'), QMessageBox.RejectRole)
        ret = msgBox.exec()

        if ret == 0:
            sort_type = SortType.SORT_BY_WORD_COUNT
        elif ret == 1:
            sort_type = SortType.SORT_BY_WORD_COUNT_REVERSE
        else:
            sort_type = SortType.SORT_BY_ALPHABETICALLY

        self.tool.produce_pron_compare_file(SortType.SORT_BY_ALPHABETICALLY)
        self.tool.check_sentence_base_file()
        self.tool.produce_pron_count_file(sort_type)
        QMessageBox.information(self,
                                '>_<',
                                '檔案產生成功!',
                                QMessageBox.Yes)

        error_sentence_base = self.tool.incorrect_sentence_base_path
        message = ''
        for key, value in error_sentence_base.items():
            message += key + '\t' + value + '\n'
        self.ui.tb_error_sentence_base.setText(message)

    def analysis_pron_count_file_click(self):
        analysis = self.tool.analysis_pron_count_file()

        message = ''
        for key, value in analysis.items():
            message += key + ':' + value + '\n'

        QMessageBox.information(self,
                                '>_<',
                                '涵蓋率分析:'
                                + '\n' + message,
                                QMessageBox.Yes)

    def calculate_sentences_file_click(self):
        source_file_path, filetype = QFileDialog. \
            getOpenFileName(self,
                            "選取句子檔案文件",
                            "./",
                            "Text Files (*.txt)")
        dest_file_path, filetype = QFileDialog. \
            getSaveFileName(self,
                            "選取文件",
                            "./",
                            "Text Files (*.txt)")
        msgBox = QMessageBox()
        msgBox.setText('積分檔案要如何排序?')
        msgBox.addButton(QPushButton('平均積分排序由小到大'), QMessageBox.YesRole)
        msgBox.addButton(QPushButton('平均積分排序由大到小'), QMessageBox.NoRole)
        ret = msgBox.exec()

        if ret == 0:
            sort_type = SortType.SORT_BY_WORD_COUNT
        elif ret == 1:
            sort_type = SortType.SORT_BY_WORD_COUNT_REVERSE

        self.tool.calculate_sentences_score(source_file_path, dest_file_path, sort_type)

        QMessageBox.information(self,
                                '>_<',
                                '積分檔案產生成功!',
                                QMessageBox.Yes)

    def calculate_sentence_click(self):
        sentence = self.ui.le_sentence.text()
        score = self.tool.calculate_sentence_score(sentence)
        self.ui.tb_sentence_score.setText(''.join(score))


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())


# word_dict_file = 'WordData_1227.txt'
# pron_compare_file = 'pron_compare.txt'
# sentence_base_dir = '文字基底/txt'
# pron_count_file = 'pron_count.txt'
#
# tool = CountScoreTool(word_dict_file, pron_compare_file,
#                       sentence_base_dir, pron_count_file)
#
# tool.produce_pron_compare_file(SortType.SORT_BY_ALPHABETICALLY)
# tool.check_sentence_base_file()
# tool.produce_pron_count_file(SortType.SORT_BY_WORD_COUNT_REVERSE)
# tool.analysis_pron_count_file()
# print(tool.calculate_sentence_score('為臨帖他還遠遊西安碑林龍門石窟泰山摩崖石刻'))
# tool.calculate_sentences_score('sentence_3000.txt', 'sentence_3000_score.txt', SortType.SORT_BY_WORD_COUNT_REVERSE)




# # words_set = {}
# # with open('pron_compare.txt', 'r', encoding='utf-8') as f:
# #     for line in f:
# #         word_lists = line.strip().split(',')[2:]
# #         for word in word_lists:
# #             if word in words_set:
# #                 words_set[word].append(''.join(line.split(',')[1:2]))
# #             else:
# #                 words_set[word] = []
# #                 words_set[word].append(''.join(line.split(',')[1:2]))
# #     update_word_set = {word: prons for word, prons in words_set.items() if len(prons) > 1}
# #
# # with open('repeated_prons.txt', 'w', encoding='utf-8') as f:
# #     for word, prons in update_word_set.items():
# #         f.write(word + ': ' + ','.join(prons))
# #         f.write('\n')
