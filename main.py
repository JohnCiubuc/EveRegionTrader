import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPlainTextEdit
import csv





class EveTrader(QWidget):

    layout = ''
    tabs = ''

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Multibuy App')
        self.setGeometry(100, 100, 800, 600)


        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        # First tab
        tab1 = QWidget()
        tab1.layout = QVBoxLayout()
        tab1.plainTextEdit = QPlainTextEdit()
        tab1.layout.addWidget(tab1.plainTextEdit)
        tab1.setLayout(tab1.layout)
        self.tabs.addTab(tab1, 'Paste your multibuy window here')


        tab1.plainTextEdit.textChanged.connect(self.process_multibuy_window)        # Second tab

        tab2 = QWidget()
        tab2.layout = QVBoxLayout()
        tab2.table = QTableWidget()
        tab2.table.setColumnCount(5)
        tab2.table.setHorizontalHeaderLabels(['Item', 'Region', 'Buy Order (Highest)', 'Sell Order (Lowest)', 'Sell Order (Average)'])
        tab2.layout.addWidget(tab2.table)
        tab2.setLayout(tab2.layout)
        self.tabs.addTab(tab2, 'Spreadsheet Viewer 1')

        # Third tab
        tab3 = QWidget()
        tab3.layout = QVBoxLayout()
        tab3.table = QTableWidget()
        tab3.table.setColumnCount(2)
        tab3.table.setHorizontalHeaderLabels(['Item ID', 'Item Name'])

        with open('type_ids.csv', 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            for row_num, row_data in enumerate(csv_reader):
                if len(row_data) >= 2:
                    tab3.table.insertRow(row_num)
                    for column_num, data in enumerate(row_data[:2]):
                        item = QTableWidgetItem(data)
                        tab3.table.setItem(row_num, column_num, item)

        tab3.layout.addWidget(tab3.table)
        tab3.setLayout(tab3.layout)
        self.tabs.addTab(tab3, 'Spreadsheet Viewer 2')

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def find_item_id(self, item_name):
        with open('type_ids.csv', 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            for row_data in csv_reader:
                if len(row_data) >= 2 and item_name.lower() in row_data[1].lower():
                    return row_data[0]
        return None

    def process_multibuy_window(self):
        first_tab = self.tabs.widget(0)
        text = first_tab.plainTextEdit.toPlainText().split('\n')
        for item in text:
            item_id = self.find_item_id(item)
            if item_id:
                print(f'Item Name: {item}, Item ID: {item_id}')

app = QApplication(sys.argv)
window = EveTrader()
window.show()
sys.exit(app.exec_())
