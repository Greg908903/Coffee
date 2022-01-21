import sqlite3
import sys

from main_ui import main_Ui
from addEditCoffeeForm_ui import addEditCoffeeForm_Ui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox


class DBSample(QMainWindow, main_Ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.openForm)
        self.read_data()

    def read_data(self):
        res = self.connection.cursor().execute("SELECT * FROM Sorts").fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название сорта', 'Степень обжарки (до 10)',
                                                    'В зернах (да или нет)', 'Описание вкуса',
                                                    'Стоимость', 'Масса в упаковке (в кг)'])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def openForm(self):
        self.secondForm = EditForm(self.connection, self.connection.cursor())
        self.secondForm.show()

    def closeEvent(self, event):
        self.connection.close()


class EditForm(QMainWindow, addEditCoffeeForm_Ui):
    def __init__(self, con, cur):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.cur = cur
        self.con = con
        self.select_data()
        self.updateButton.clicked.connect(self.select_data)
        self.deleteButton.clicked.connect(self.delete_elem)
        self.saveButton.clicked.connect(self.save_res)
        self.addButton.clicked.connect(self.add_sort)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.titles = [description[0] for description in cur.description]
        self.modified = {}
        self.read = 0

    def add_sort(self):
        self.cur.execute('''INSERT INTO Sorts(name, degreeRoast) VALUES('имя по умолчанию', 0)''')
        self.select_data()

    def save_res(self):
        if self.modified:
            for i in self.modified:
                que = "UPDATE Sorts SET\n"
                que += ", ".join([f"{key}='{self.modified[i][key]}'"
                                  for key in self.modified[i].keys()])
                que += "WHERE id = ?"
                # print(que)
                self.cur.execute(que, (i,))
            self.con.commit()
            self.modified.clear()

    def item_changed(self, item):
        if self.read:
            return
        key = self.tableWidget.item(item.row(), 0)
        if int(key.text()) not in self.modified:
            self.modified[int(key.text())] = {}
        self.modified[int(key.text())][self.titles[item.column()]] = item.text()

    def delete_elem(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.cur.execute("DELETE FROM Sorts WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
        self.select_data()

    def select_data(self):
        self.read = 1
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        res = self.cur.execute("SELECT * FROM Sorts").fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название сорта', 'Степень обжарки (до 10)',
                                                    'В зернах (да или нет)', 'Описание вкуса',
                                                    'Стоимость', 'Масса в упаковке (в кг)'])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.read = 0

    def closeEvent(self, event) -> None:
        ex.read_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())
