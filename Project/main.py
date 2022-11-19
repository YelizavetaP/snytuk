import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
import json
from PyQt5 import QtGui

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        path = r'C:\\Users\ASUS\labs\EO\eo_rep\EOlabs2022\Project\main.ui'
        loadUi(path, self)
        
        self.fill_zero()
             
        self.load_data.clicked.connect(self.readData)
        self.changeCount.clicked.connect(self.changeRowColCount)
        self.browseFileButton.clicked.connect(self.browseFile)

        self.distanceTable.itemChanged.connect(self.changeIcon)



    def changeIcon(self, item):
        row = item.row()
        col = item.column()
        widjetItem = self.distanceTable.item(row, col)

        if (row < col):
            self.distanceTable.setItem(col, row, QtWidgets.QTableWidgetItem(str(widjetItem.text())))
       


        
    def changeRowColCount(self):
        self.distanceTable.setRowCount(int(self.rowCount.text()))
        self.distanceTable.setColumnCount(int(self.rowCount.text()))
        self.parcelsTable.setRowCount(int(self.rowCount.text()))

        self.fill_zero()

    def browseFile(self):
        data = self.open_dialog_box()
        print(data)

        self.distanceTable.setRowCount(int(data['p']))
        self.distanceTable.setColumnCount(int(data['p']))
        self.parcelsTable.setRowCount(int(data['p']))

        self.fill_zero()

        for row in range(self.distanceTable.rowCount()):
            for col in range(self.distanceTable.columnCount()):
                item = data['distance']
                self.distanceTable.setItem(row, col, QtWidgets.QTableWidgetItem(str(item[row][col])))

        for row in range(self.parcelsTable.rowCount()):
            for col in range(self.parcelsTable.columnCount()):
                item = data['parcels']
                self.parcelsTable.setItem(row, col, QtWidgets.QTableWidgetItem(str(item[row][col])))

        self.n.setText(str(data['n']))
        self.m.setText(str(data['m']))
        self.vk.setText(str(data['vk']))
        self.va.setText(str(data['va']))
        self.k_pay.setText(str(data['k_pay']))
        self.a_pay.setText(str(data['a_pay']))

    def open_dialog_box(self):
        filepath = QFileDialog.getOpenFileName()[0]
        print(filepath)

        with open(filepath, 'r') as f:
            data = json.load(f)
            # print(f.readline())
            return data


    def readData(self):

        distance, parcels = [], []
        n = int(self.n.text())
        m = int(self.m.text())
        p = self.distanceTable.columnCount() #кількість посилок

        vk = float(self.vk.text())
        va = float(self.va.text())

        k_pay = float(self.k_pay.text())
        a_pay = float(self.a_pay.text())

        print(n, m, p, vk, va, k_pay, a_pay)

        for row in range(self.distanceTable.rowCount()):
            rowData = []
            for col in range(self.distanceTable.columnCount()):
                widjetItem = self.distanceTable.item(row, col)
                print(widjetItem)
                if (widjetItem and widjetItem.text):
                    rowData.append(float(widjetItem.text()))
                else: rowData.append('')
            distance.append(rowData)
        print(distance)

        for row in range(self.parcelsTable.rowCount()):
            rowData = []
            for col in range(self.parcelsTable.columnCount()):
                widjetItem = self.parcelsTable.item(row, col)
                if (widjetItem and widjetItem.text):
                    rowData.append(float(widjetItem.text()))
                else: rowData.append('')
            parcels.append(rowData)
        print(parcels)
    
        return distance, parcels, n, m, p, vk, va, k_pay, a_pay
    


    # 0 по діагоналі
    def fill_zero(self):        
        for row in range(self.distanceTable.columnCount()):
            self.distanceTable.setRowHeight(row,50)
            self.parcelsTable.setRowHeight(row, 50)
            for col in range(self.distanceTable.columnCount()):
                self.distanceTable.setColumnWidth(col,50)
                if(row == col): 
                    self.distanceTable.setItem(row, col, QtWidgets.QTableWidgetItem('0'))
                    self.distanceTable.item(row, col).setBackground(QtGui.QColor(232,236,235))
            
            for col in range(self.parcelsTable.columnCount()):
                self.parcelsTable.setColumnWidth(col,80)

        
        
            





    # def loadData(self):
    #     address = [
    #         {"1":'2', '2': 20, '3': 30, '4':40},
    #         {'2':20, '2': '', '3': 50, '4':70},
    #         {'3':30, '2': 50, '3': '', '4':30},
    #         {'4':40, '2': 70, '3': 30, '4': ''}
    #     ]
    #     row = 0
    #     for a in address:
    #         self.tableWidget.setItem(row, 0, QTableWidgetItem(a["1"]))
    #         row += 1       


app = QApplication(sys.argv)
mainwindow = MainWindow()
widjet = QtWidgets.QStackedWidget()
widjet.addWidget(mainwindow)
widjet.setMinimumSize(1150,850)

widjet.show()

try:
    sys.exit(app.exec_())
except:
    print('Exiting')