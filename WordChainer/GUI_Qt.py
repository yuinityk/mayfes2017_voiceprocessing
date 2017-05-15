# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pygame
from pygame.locals import *
import sys
import time
import Shiritori
import jtalk



class PicButton(QAbstractButton):
    def __init__(self, text, pixmap, pixmap_hover, pixmap_pressed, parent=None):
        super(PicButton, self).__init__(parent)
        self.setText(text)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(200, 200)


class WaitDialog(QDialog):

    def __init__(self, parent=None):
        super(WaitDialog, self).__init__(parent)
        font = QFont()
        font.setPointSize(10)
        # label1 = QLabel("録音中...")
        # label1.setFont(font)
        # layout = QVBoxLayout()
        # layout.addWidget(label1)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("録音中...")
        self.resize(200, 100)
        # self.setLayout(layout)
        self.setModal(True)
        self.show()
        self.raise_()
        QApplication.processEvents()


class MenuWidget(QWidget):

    def __init__(self, parent=None):

        super(MenuWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):

        label = QLabel('難易度を選んでね!')
        font = QFont()
        font.setPointSize(30)
        label.setFont(font)
        hlayout = QHBoxLayout()
        hlayout.addStretch(1)
        hlayout.addWidget(label)
        hlayout.addStretch(1)

        #self.button1 = PicButton('easy', QPixmap("a.png"), QPixmap("b.png"), QPixmap("c.png"))
        self.button1 = QPushButton('easy')
        self.button2 = QPushButton('normal')
        self.button3 = QPushButton('hard')
        self.button4 = QPushButton('reverse')
        self.button1.setToolTip('かんたーん')
        self.button2.setToolTip('ふつう')
        self.button3.setToolTip('すごーいむずかしい')
        self.button4.setToolTip('あたまとり')
        # button1.setIcon(QIcon("easy.png"))
        # button2.setIcon(QIcon("normal.png"))
        # button3.setIcon(QIcon("hard.png"))
        # button4.setIcon(QIcon("reverse.png"))

        layout = QHBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)

        vlayout = QVBoxLayout()
        vlayout.addStretch(1)
        vlayout.addLayout(hlayout)
        vlayout.addStretch(2)
        vlayout.addLayout(layout)
        vlayout.addStretch(2)

        self.setLayout(vlayout)


class RecordWidget(QWidget):

    def __init__(self, parent=None):
        super(RecordWidget, self).__init__(parent)

        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(40)
        self.player = QLineEdit()
        self.PC = QLineEdit()
        label1 = QLabel("あなた")
        label2 = QLabel("PC")
        self.player.setFont(font)
        self.PC.setFont(font)
        label1.setFont(font)
        label2.setFont(font)
        lineLayout = QGridLayout()
        lineLayout.addWidget(label1, 0, 0)
        lineLayout.addWidget(self.player, 0, 1)
        lineLayout.addWidget(label2, 1, 0)
        lineLayout.addWidget(self.PC, 1, 1)
        lineLayout.setSpacing(50)
        self.word_text = QTextEdit()
        self.cursor = self.word_text.textCursor()
        self.record_button = QPushButton('record')

        recordLayout = QVBoxLayout()
        recordLayout.addStretch(2)
        recordLayout.addLayout(lineLayout)
        recordLayout.addStretch(1)
        recordLayout.addWidget(self.word_text)
        recordLayout.addWidget(self.record_button)
        recordLayout.addStretch(2)

        mainLayout = QHBoxLayout()
        mainLayout.addStretch(1)
        mainLayout.addLayout(recordLayout)
        mainLayout.addStretch(1)

        # self.recording_msg = QMessageBox()
        # self.recording_msg.setWindowTitle('ちょっと待ってね')
        # self.recording_msg.setText('録音中…')
        # self.recording_msg.setStandardButtons(self.recording_msg.NoButton)

        self.setLayout(mainLayout)


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.initUI()
        self.play = Play(30)
        #self.word_list = []

    def initUI(self):
        self.setWindowTitle('WordChainer')
        self.menu = MenuWidget(self)
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.menu)
        self.setLayout(self.vbox)
        self.menu.button1.clicked.connect(self.record_handler)
        self.menu.button2.clicked.connect(self.record_handler)
        self.menu.button3.clicked.connect(self.record_handler)
        self.menu.button4.clicked.connect(self.record_handler)
        #self.setFixedSize(800, 500)
        self.showFullScreen()

    def record_handler(self):
        self.menu.close()
        sender = self.sender()
        self.play.set_difficulty(sender.text())
        self.record = RecordWidget(self)
        self.vbox.addWidget(self.record)
        self.setLayout(self.vbox)
        self.record.record_button.clicked.connect(self.play_handler)

    def play_handler(self):
        #self.record.recording_msg.exec_()
        #QApplication.processEvents()
        recording = WaitDialog()
        self.play.voice_record()
        self.play.playerschead, self.play.playersctail = self.play.word_recognize()
        self.play.playersentence = self.play.get_sentence()
        #self.record.recording_msg.close()
        recording.close()
        if self.play.playersentence != "":
            self.record.player.setText(self.play.playersentence)
            #self.word_list.append(self.play.playersentence)
            self.play.is_pcturn = True
            self.play.is_noinputerror = False
            r = self.play.respond()
            if self.play.notsflag == 1:
                if self.play.difficulty == 'reverse':
                    QMessageBox.warning(self, 'おっと', 'あたまをとろう！')
                else:
                    QMessageBox.warning(self, 'おっと', 'しりをとろう！')
            elif r == 'win':
                QMessageBox.about(self, 'WIN', 'すごーい!あなたの勝ちだよ!')
                self.close()
                self.__init__()
            elif r == 'lose':
                QMessageBox.about(self, 'LOSE', 'ざんねん…')
                self.close()
                self.__init__()
            else:
                self.record.cursor.insertText(self.play.playersentence + ' -> ')
                self.record.PC.setText(self.play.pcword)
                self.record.cursor.insertText(self.play.pcword + ' -> ')
                #self.word_list.append(self.play.pcword)
        else:
            self.play.is_pcturn = False
            QMessageBox.warning(self, '聞き取れなかった…', 'なにか話して!')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class Play:
    def __init__(self, fps):
        self.fps = fps
        self.difficulty = 'easy'
        self.is_pcturn = False
        self.is_noinputerror = False
        self.counter = int(3 * 1000. / fps)
        self.pcword = ''
        self.playerword = ''
        self.playerschead = ''
        self.playersctail = ''
        self.playersentence = ''
        self.pcword_former = ''
        self.pcsctail = ''
        self.wdic = {}
        self.notsflag = 0  # 1のときしりをとっていない
        # self.rec = pygame.image.load("button_s.png").convert_alpha()
        # self.recording = pygame.font.Font(myfont, 40).render('録音中...', True, (0,0,0))
        # self.thinking = pygame.font.Font(myfont, 40).render('考え中...', True, (0,0,0))

    def update(self, playerword):
        self.playerword = playerword

    def respond(self):
        if self.is_noinputerror == True:
            return ''
        self.pcword_former = self.pcword
        if self.playersctail in ['ん', 'ン']:
            return 'lose'
        #savedic = Shiritori.learn_word(self.playerword,{})
        # Shiritori.save_dic(savedic)
        # とりあえず辞書の更新はやめる
        if len(self.wdic[self.playersctail]) == 0:
            return 'win'
        # if self.pcword_former != '' and
        # Shiritori.to_katakana(self.playerword[0]) !=
        # Shiritori.to_katakana(Shiritori.get_endletter(self.pcword_former)):
        if self.pcword_former != '' and self.playerschead != self.pcsctail:
            self.notsflag = 1
        else:
            re = Shiritori.return_word(self.playersctail, self.wdic)
            self.pcword = re
            if self.difficulty != 'reverse':
                self.pcsctail = Shiritori.get_endletter(self.pcword)
            else:
                self.pcsctail = self.pcword[0]
            self.wdic[self.playersctail].remove(re)
            self.notsflag = 0
            # jtalk.jtalk(re.encode('utf-8'))
            return ''

    def load_dic(self):
        pass

    def voice_record(self):
        Shiritori.record()

    def get_sentence(self):
        sent = Shiritori.get_sentence()
        if sent != '_on':
            return sent
        else:
            return ""

    def word_recognize(self):
        #w = Shiritori.word_recognize(self.difficulty)
        head, tail = Shiritori.get_headntail(self.difficulty)
        if head != '_on' and tail != '_on':
            return head, tail
        else:
            self.is_noinputerror = True
            return '', ''

    def set_difficulty(self, d):
        self.difficulty = d
        self.wdic = Shiritori.load_dic(d)
        # print(self.wdic.keys())

    def reset(self):
        self.is_pcturn = False
        self.pcword = ''
        self.playerword = ''
        self.pcword_former = ''
        self.wdic = {}


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
