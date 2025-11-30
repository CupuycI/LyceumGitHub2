import sqlite3
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QHeaderView
from PyQt6 import uic


class MainWD(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.coffee_db = sqlite3.connect('coffee.sqlite')
        self.cur = self.coffee_db.cursor()
        self.tableWidget: QTableWidget
        result = self.cur.execute('SELECT * FROM Coffee').fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setHorizontalHeaderLabels(['Название', "Сорт", "Степень обжарки", "Тип", "Описание вкуса",
                                                    "Стоимость", "Объём"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        for r, row in enumerate(result):
            for c, col in enumerate(row[1:]):
                item = QTableWidgetItem(str(col))
                self.tableWidget.setItem(r, c, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = MainWD()
    wd.show()
    sys.exit(app.exec())