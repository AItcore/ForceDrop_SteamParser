from parser import ParserSite
import sqlite3
from PyQt5.Qt import QTimer
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QPushButton, QHBoxLayout,
    QVBoxLayout, QListWidget, QLabel)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("Account.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.parser = ParserSite()
        self.createBD()
        # self.conn.
        self.initUI()
        self.isActive = False

    def startParse(self):
        if not (self.isActive and self.parser.isAlive()):
            self.isActive = True
            try:
                self.parser.start()
            except Exception:
                self.parser = ParserSite()
                self.parser.start()

    def initUI(self):
        self.setFixedSize(800, 600)
        self.setWindowTitle("ForceDrop Steam Accounts")

        self.listBox = QListWidget(self)
        self.listBox.setObjectName("listBox")
        self.listBox.setMaximumSize(QSize(350, 9999))
        self.listBox.setMinimumSize(QSize(350, 0))

        self.startBtn = QPushButton(parent=self, text="Старт")
        self.stopBtn = QPushButton(parent=self, text="Стоп")
        self.refreshBtn = QPushButton(parent=self, text="Обновить список")
        self.isWorkLbl = QLabel(parent=self, text="Не работает")

        self.urlLabel = QLabel(parent=self, text="Ссылка на профиль: ")
        self.urlLabel.setWordWrap(True)
        self.urlLabel.setOpenExternalLinks(True)

        self.frcdrpLabel = QLabel(parent=self, text="Ссылка на ForceDrop: ")
        self.frcdrpLabel.setWordWrap(True)
        self.frcdrpLabel.setOpenExternalLinks(True)

        self.accountPrice = QLabel(parent=self, text="Стоймость аккаунта: ")
        self.IsBan = QLabel(parent=self, text="Бан на трейд: ")
        self.hoursPlay = QLabel(parent=self, text="Часов наигранно")

        self.NickLabel = QLabel(parent=self, text="Имя профиля: ")
        self.lvlLabel = QLabel(parent=self, text="Уровень профиля: ")
        self.lastOnlineLabel = QLabel(parent=self, text="Последний раз онлайн: ")

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.addWidget(self.listBox)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.addWidget(self.urlLabel)
        self.verticalLayout.addWidget(self.frcdrpLabel)
        self.verticalLayout.addWidget(self.NickLabel)
        self.verticalLayout.addWidget(self.accountPrice)
        self.verticalLayout.addWidget(self.lvlLabel)
        self.verticalLayout.addWidget(self.lastOnlineLabel)
        self.verticalLayout.addWidget(self.IsBan)
        self.verticalLayout.addWidget(self.hoursPlay)

        self.btnLayout = QHBoxLayout()
        self.btnLayout.addWidget(self.isWorkLbl)
        self.btnLayout.addWidget(self.refreshBtn)
        self.btnLayout.addWidget(self.stopBtn)
        self.btnLayout.addWidget(self.startBtn)

        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout.addLayout(self.btnLayout)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.aliveParser)
        self.timer.start()
        self.startBtn.clicked.connect(self.startParse)
        self.stopBtn.clicked.connect(self.parserEndWork)
        self.refreshBtn.clicked.connect(self.refreshList)
        self.listBox.clicked.connect(self.clickListElem)
        self.show()

    def refreshList(self):
        self.listBox.clear()
        self.cursor.execute(
            "SELECT nick FROM accounts WHERE is_ban_trade='False'")
        count = 0
        for item in self.cursor.fetchall():
            self.listBox.insertItem(count, item[0])
            count += 1

    def clickListElem(self):
        elem = self.listBox.currentItem()
        sql = "SELECT * FROM accounts WHERE url='http://steamcommunity.com/profiles/"+str(elem.text()) + "';"
        account = self.cursor.execute(sql).fetchone()
        ban = ""
        if account[5] == "False":
            ban = "Нету"
        else:
            ban = "Есть"
        self.urlLabel.setText("Ссылка на профиль: <a href =" + account[1] + ">"+account[1]+"<a>")
        self.accountPrice.setText("Стоймость аккаунта: " + str(round(float(account[2].split()[0])/75,2)) + "$")
        self.hoursPlay.setText("Часов наигранно: \nCS:GO: "+account[3] + " ч.\nDOTA 2: " + account[4] + " ч.")
        self.IsBan.setText("Бан на трейд: " + ban)

    def createBD(self):
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS accounts(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            url TEXT,
            forcedrop_url TEXT
            items_price TEXT,
            csgo_hours TEXT,
            dota2_hours TEXT,
            is_ban_trade TEXT,
            nick TEXT,
            lvl TEXT,
            last_online TEXT
        );
        """)

    def parserEndWork(self):
        self.parser.end_work()
        self.isEnabled = False
        if self.parser.isAlive():
            self.parser.join()
        else:
            self.parser.parserQuit()
        self.isActive = False
        self.isEnabled = True

    def aliveParser(self):
        if self.parser.isAlive():
            self.isWorkLbl.setText("Работает")
        else:
            self.isWorkLbl.setText("Не работает")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 'Точно хочешь выйти?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.hide()
            self.timer.stop()
            self.parserEndWork()
            event.accept()
        else:
            event.ignore()
