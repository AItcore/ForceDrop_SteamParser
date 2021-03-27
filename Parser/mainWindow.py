from ParserSite import ParserSite
import sqlite3
from PyQt5.Qt import QTimer
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QPushButton, QHBoxLayout,
    QVBoxLayout, QListWidget, QLabel, QLineEdit, QComboBox)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("Account.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.choosenSite = "https://ggdrop.one/"
        self.parser = ParserSite(self.choosenSite)
        self.createBD()
        self.lastItem = None
        self.initUI()
        self.isActive = False

    def startParse(self):
        if not (self.isActive and self.parser.isAlive()):
            self.isActive = True
            try:
                if self.siteCBox.currentText() == "ForceDrop":
                    self.parser = ParserSite("https://forcedrop.top/")
                    self.parser.start()
                elif self.siteCBox.currentText() == "GGDrop":
                    self.parser = ParserSite("https://ggdrop.one/")
                    self.parser.start()
            except Exception:
                pass

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

        self.frcdrpLabel = QLabel(parent=self, text="Ссылка на : ")
        self.frcdrpLabel.setWordWrap(True)
        self.frcdrpLabel.setOpenExternalLinks(True)

        self.accountPrice = QLabel(parent=self, text="Стоймость аккаунта: ")
        self.IsBan = QLabel(parent=self, text="Бан на трейд: ")
        self.hoursPlay = QLabel(parent=self, text="Часов наигранно: ")

        self.NickLabel = QLabel(parent=self, text="Имя профиля: ")
        self.lvlLabel = QLabel(parent=self, text="Уровень профиля: ")
        self.lastOnlineLabel = QLabel(
            parent=self, text="Последний раз онлайн: ")
        self.countFriends = QLabel(parent=self, text="Количество друзей: ")

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
        self.verticalLayout.addWidget(self.countFriends)

        self.btnLayout = QHBoxLayout()
        self.btnLayout.addWidget(self.isWorkLbl)
        self.btnLayout.addWidget(self.refreshBtn)
        self.btnLayout.addWidget(self.stopBtn)
        self.btnLayout.addWidget(self.startBtn)

        self.priceLabel = QLabel("Цена:", self)
        self.priceEdit = QLineEdit("", self)
        self.nickLabel = QLabel("Никнейм:", self)
        self.nickEdit = QLineEdit("", self)
        self.nickEdit.textEdited.connect(self.nickEnter)
        self.siteLabel = QLabel("Сайт:",self)
        self.siteCBox = QComboBox(self)
        self.siteCBox.addItem("ForceDrop")
        self.siteCBox.addItem("GGDrop")

        self.filterLayout = QHBoxLayout()
        self.filterLayout.addWidget(self.priceLabel)
        self.filterLayout.addWidget(self.priceEdit)
        self.filterLayout.addWidget(self.nickLabel)
        self.filterLayout.addWidget(self.nickEdit)
        self.filterLayout.addWidget(self.siteLabel)
        self.filterLayout.addWidget(self.siteCBox)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout.addLayout(self.filterLayout)
        self.verticalLayout.addLayout(self.btnLayout)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.aliveParser)
        self.timer.start()

        self.clickTimer = QTimer(self)
        self.clickTimer.setInterval(10)
        self.clickTimer.timeout.connect(self.clickListElem)
        self.clickTimer.start()

        self.startBtn.clicked.connect(self.startParse)
        self.stopBtn.clicked.connect(self.parserEndWork)
        self.refreshBtn.clicked.connect(self.refreshList)
        self.show()
        self.refreshList()

    def refreshList(self):
        self.listBox.clear()
        try:
            self.cursor.execute(
                "SELECT nick, items_price FROM accounts \
                    WHERE is_ban_trade='False' and items_price !='0 руб.'")
            count = 0
            for item in self.cursor.fetchall():
                if self.priceEdit.text() == "":
                    self.listBox.insertItem(count, item[0])
                    count += 1
                elif round(float(item[1].split()[0])/75, 2) > int(self.priceEdit.text()):
                    self.listBox.insertItem(count, item[0])
                    count += 1
        except Exception:
            pass

    def clickListElem(self):
        elem = self.listBox.currentItem()
        if elem is not None and not elem == self.lastItem:
            self.lastItem = elem
            try:
                sql = "SELECT * FROM accounts WHERE nick=\"" + \
                    str(elem.text())+"\";"
                account = self.cursor.execute(sql).fetchone()
                siteURL = ''
                if 'forcedrop' in account[2]:
                    siteURL = "ForceDrop"
                else:
                    siteURL = "GGDrop"
                ban = ""
                if account[6] == "False":
                    ban = "Нету"
                else:
                    ban = "Есть"
                self.urlLabel.setText(
                    "Ссылка на профиль: <a href =" + account[1] + ">"+account[1]+"<a>")
                self.accountPrice.setText(
                    "Стоймость аккаунта: " + str(round(float(account[3].split()[0])/75, 2)) + "$")
                self.hoursPlay.setText(
                    "Часов наигранно: \nCS:GO: " + account[4] + " ч.\nDOTA 2: " + account[5] + " ч.")
                self.IsBan.setText("Бан на трейд: " + ban)
                self.frcdrpLabel.setText(
                    "Ссылка на " + siteURL + ": <a href="+account[2] + ">" + account[2] + "<a>")
                self.NickLabel.setText("Имя профиля: "+account[7])
                self.lvlLabel.setText("Уровень профиля: "+account[8])
                self.lastOnlineLabel.setText("Последний раз онлайн: "+account[9])
                self.countFriends.setText("Количество друзей: " + account[10])
            except Exception:
                pass

    def createBD(self):
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS accounts(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            url TEXT,
            forcedrop_url TEXT,
            items_price TEXT,
            csgo_hours TEXT,
            dota2_hours TEXT,
            is_ban_trade TEXT,
            nick TEXT,
            lvl TEXT,
            last_online TEXT,
            friend_count TEXT
        );
        """)

    def nickEnter(self):
        self.listBox.clear()
        try:
            self.cursor.execute(
                "SELECT nick, items_price FROM accounts WHERE \
                is_ban_trade='False' and items_price !='0 руб.' \
                    and nick LIKE ?", ['%'+self.nickEdit.text()+'%'])
            count = 0
            for item in self.cursor.fetchall():
                self.listBox.insertItem(count, item[0])
                count += 1
        except Exception:
            pass

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

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            elem = self.listBox.currentItem()
            row = self.listBox.row(elem)
            self.listBox.takeItem(row)
            self.cursor.execute(
                "DELETE FROM accounts WHERE nick=\"" + elem.text() + "\"")
            self.conn.commit()
