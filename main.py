import sqlite3
import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QHeaderView, QWidget
from UI import mainUI, addEditCoffeeFormUI


def get_appdata_path(appname):
    if sys.platform == "win32":
        path = os.path.join(os.environ['APPDATA'], appname)
    elif sys.platform == "darwin":
        path = os.path.join(os.path.expanduser("~"), "Library", "Application Support", appname)
    else:
        path = os.path.join(os.path.expanduser("~"), ".local", "share", appname)

    if not os.path.exists(path):
        os.makedirs(path)

    return path


class MainWD(QMainWindow, mainUI.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.load_db()
        self.update_table()
        self.add_btn.clicked.connect(self.add_coffee)
        self.edit_btn.clicked.connect(self.edit_coffee)

    def load_db(self):
        path = os.path.join(get_appdata_path('Coffee'), 'DATA')
        if not os.path.exists(path):
            os.makedirs(path)
            path = os.path.join(path, 'coffee.sqlite')
            self.coffee_db = sqlite3.connect(path)
            self.cur = self.coffee_db.cursor()
            self.cur.execute("""CREATE TABLE Coffee(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sort TEXT NOT NULL,
            roasting INT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            cost INT NOT NULL,
            volume TEXT NOT NULL)""")
            self.coffee_db.commit()
            return

        path = os.path.join(path, 'coffee.sqlite')

        self.coffee_db = sqlite3.connect(path)
        self.cur = self.coffee_db.cursor()

    def update_table(self):
        result = self.cur.execute('SELECT * FROM Coffee').fetchall()
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название', "Сорт", "Степень обжарки", "Тип",
                                                    "Описание вкуса", "Стоимость", "Объём"])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        for r, row in enumerate(result):
            for c, col in enumerate(row):
                item = QTableWidgetItem(str(col))
                self.tableWidget.setItem(r, c, item)

        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def add_coffee(self):
        self.form = addEditCoffee('add', self)
        self.form.show()

    def edit_coffee(self):
        if not self.tableWidget.selectedItems():
            return

        self.form = addEditCoffee('edit', self)
        self.form.show()


class addEditCoffee(QWidget, addEditCoffeeFormUI.Ui_Form):
    def __init__(self, task, wd):
        super().__init__()
        self.setupUi(self)
        self.wd = wd

        if task == 'add':
            self.accept.clicked.connect(self.add_coffee)

        elif task == 'edit':
            self.accept.clicked.connect(self.edit_coffee)
            result = wd.tableWidget.selectedItems()
            self.id_ = int(result[0].text())
            self.name.setText(result[1].text())
            self.sort.setText(result[2].text())
            self.roasting.setCurrentText(result[3].text())
            self.type.setCurrentText(result[4].text())
            self.description.setPlainText(result[5].text())
            self.cost.setText(result[6].text())
            volume = result[7].text().split()
            self.volume.setText(volume[0])
            self.volume_comboBox.setCurrentText(volume[1])

    def get_verdict(self):
        if not self.name.text().strip():
            return False

        if not self.sort.text().strip():
            return False

        if not self.cost.text().strip().isdigit():
            return False

        if not self.volume.text().strip().isdigit():
            return False

        return True

    def add_coffee(self):
        if not self.get_verdict():
            return

        parameters = {
            'name': self.name.text().strip(),
            'sort': self.sort.text().strip(),
            'roasting': int(self.roasting.currentText()),
            'type': self.type.currentText(),
            'description': self.description.toPlainText(),
            'cost': int(self.cost.text().strip()),
            'volume': ' '.join([self.volume.text().strip(), self.volume_comboBox.currentText()])
        }
        self.wd.cur.execute("""INSERT INTO Coffee(name, sort, roasting, type, description, cost, volume)
        VALUES(:name, :sort, :roasting, :type, :description, :cost, :volume)""", parameters)
        self.wd.coffee_db.commit()
        self.wd.update_table()
        self.close()

    def edit_coffee(self):
        if not self.get_verdict():
            return

        parameters = {
            'name': self.name.text().strip(),
            'sort': self.sort.text().strip(),
            'roasting': int(self.roasting.currentText()),
            'type': self.type.currentText(),
            'description': self.description.toPlainText(),
            'cost': int(self.cost.text().strip()),
            'volume': ' '.join([self.volume.text().strip(), self.volume_comboBox.currentText()]),
            'id': self.id_
        }
        self.wd.cur.execute("""UPDATE Coffee
        SET name = :name, sort = :sort, roasting = :roasting, type = :type, description = :description,
        cost = :cost, volume = :volume
        WHERE id = :id""", parameters)
        self.wd.coffee_db.commit()
        self.wd.update_table()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = MainWD()
    wd.show()
    sys.exit(app.exec())