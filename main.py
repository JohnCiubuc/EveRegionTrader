import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPlainTextEdit, QPushButton, QHeaderView, QRadioButton, QButtonGroup
from PyQt5.QtGui import QColor
import csv
import requests

def convert_to_currency(num):
    try:
        num = float(num)
        return "${:,.2f}".format(num)
    except ValueError:
        return "Invalid input. Please enter a valid number."


def interpolate_color(value):
    red = QColor(255, 0, 0)
    blue = QColor(0, 0, 255)

    r = red.red() + (blue.red() - red.red()) * value
    g = red.green() + (blue.green() - red.green()) * value
    b = red.blue() + (blue.blue() - red.blue()) * value

    return QColor(int(r), int(g), int(b))

class EveTrader(QWidget):

    layout = ''
    tabs = ''
    item_ids = ''
    csv_reader = ''


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


        radio_button_1 = QRadioButton('Dodixie')
        radio_button_2 = QRadioButton('Amarr')

        self.button_group = QButtonGroup()
        self.button_group.addButton(radio_button_1, 1)
        self.button_group.addButton(radio_button_2, 2)

        tab1.layout.addWidget(radio_button_1)
        tab1.layout.addWidget(radio_button_2)

        tab1.plainButton = QPushButton()
        tab1.plainButton.setText("Grab Latest Prices")
        tab1.layout.addWidget(tab1.plainButton)
        tab1.setLayout(tab1.layout)
        self.tabs.addTab(tab1, 'Paste your multibuy window here')


        tab1.plainButton.clicked.connect(self.collect_and_process_data)        # Second tab

        tab2 = QWidget()
        tab2.layout = QVBoxLayout()
        tab2.table = QTableWidget()
        tab2.table.setAlternatingRowColors(True)
        tab2.table.setColumnCount(7)
        tab2.table.setHorizontalHeaderLabels(['Item', 'Region', 'Sell Order (Lowest)', 'Buy Order (Highest)', 'Sell Order (Average)', 'Raw Difference', 'Raw ROI'])
        tab2.layout.addWidget(tab2.table)
        tab2.setLayout(tab2.layout)
        self.tabs.addTab(tab2, 'Price Viewer')
        for i in range (0,7):
            tab2.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
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
        self.tabs.addTab(tab3, 'Item IDs (Internal)')

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.init_item_ids()

    def init_item_ids(self):
        with open('type_ids.csv', 'r') as file:
            self.csv_reader = list(csv.reader(file, delimiter=';'))

    def collect_and_process_data(self):
        radio_select_id = self.button_group.checkedId()

        item_ids, item_names = self.process_multibuy_window()
        tab2 = self.tabs.widget(1)

        item_ids_str = ','.join(item_ids)

        templates = ((f'https://market.fuzzwork.co.uk/aggregates/?region=60011866&types={item_ids_str}', 'Dodixie'),
                     (f'https://market.fuzzwork.co.uk/aggregates/?region=30002187&types={item_ids_str}', 'Amarr')
        )

        url_regions = [templates[radio_select_id-1][0],
                       f'https://market.fuzzwork.co.uk/aggregates/?region=30000142&types={item_ids_str}']

        regions_name = [templates[radio_select_id-1][1], 'Jita']

        # Clear existing rows in the table
        tab2.table.setRowCount(0)

        regions_coalesce = []

        for url_region in url_regions:
            response_region = requests.get(url_region)

            if response_region.status_code == 200:
                regions_coalesce.append(response_region.json())

            else:
                print('Error fetching data from the URL')


        if len(regions_coalesce) == 0:
            print('Error, no regions were succesfully fetched')
            return

        compare_region = regions_coalesce[0]
        for region_i, region in enumerate(regions_coalesce):
            for index, (item_id, data) in enumerate(region.items()):
                item_name = item_names[item_ids.index(item_id)]
                tab2.table.insertRow(index)

                root_value = float(compare_region[item_id]['sell']['min'])
                comp_value = float(data['sell']['min'])

                if root_value == 0:
                    continue


                diff = abs(root_value - comp_value)
                calc_tax = 0.0173+0.0448

                if root_value > comp_value and comp_value > 0:
                    roi = ((root_value * (1 - calc_tax)) - comp_value) / comp_value
                else:
                    roi = ((comp_value * (1 - calc_tax)) - root_value) / root_value

                roi_color = roi
                if roi > 0.5 or diff > 2000000:
                    roi_color = 1
                elif roi < 0:
                    roi_color = 0

                if diff < 500000 and region_i != 0:
                    continue

                roi_color = interpolate_color(roi_color)
                item = QTableWidgetItem(item_name)
                if diff != 0:
                    item.setBackground(roi_color)
                tab2.table.setItem(index, 0, item)  # Item Name
                tab2.table.setItem(index, 1, QTableWidgetItem(regions_name[region_i]))  # Region - 60011866
                tab2.table.setItem(index, 2, QTableWidgetItem(convert_to_currency(data['sell']['min'])))  # Sell Order (Lowest) - Region 60011866
                tab2.table.setItem(index, 3, QTableWidgetItem(convert_to_currency(data['buy']['max'])))  # Buy Order (Highest) - Region 60011866
                tab2.table.setItem(index, 4, QTableWidgetItem(convert_to_currency(data['sell']['weightedAverage'])))  # Sell Order (Average) - Region 60011866
                tab2.table.setItem(index, 5, QTableWidgetItem("${:,.2f}".format(diff)))  # Sell Order (Average) - Region 60011866
                if roi > 0:
                    tab2.table.setItem(index, 6, QTableWidgetItem("{:,.2f}%".format(roi*100)))  # Sell Order (Average) - Region 60011866
                print(f'Item Name: {item_name}, Item ID: {item_id}')  # Debug print
                print("${:,.2f}".format(diff))
                # Sort the rows by the first column (Item Name)
        tab2.table.sortItems(0, 0)  # Sort by the first column ascending
        self.tabs.setCurrentIndex(1)

    def find_item_id(self, item_name):
        # print(self.csv_reader)
        for row_data in self.csv_reader:
            if len(row_data) >= 2 and item_name.lower() in row_data[1].lower():
                return row_data[0]
        return None

    def process_multibuy_window(self):
        first_tab = self.tabs.widget(0)
        text = first_tab.plainTextEdit.toPlainText().split('\n')
        item_ids = []  # Store item ids for later use
        item_names = []  # Store item names for later use
        for item in text:
            item_id = self.find_item_id(item)
            if item_id:
                item_ids.append(item_id)
                item_names.append(item)

        return item_ids, item_names

app = QApplication(sys.argv)
window = EveTrader()
window.show()
sys.exit(app.exec_())
