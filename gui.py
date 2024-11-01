# gui.py
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer
import sqlite3
from main import main


DB_NAME = 'media_monitoring.db'

class MediaMonitoringGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Monitoring Suggestions")
        self.setGeometry(300, 200, 800, 500)

        # Set up central widget and layout
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Add toolbar with refresh button
        self.toolbar = QtWidgets.QToolBar("Toolbar", self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)

        refresh_icon = QtGui.QIcon.fromTheme("view-refresh")
        self.refresh_button = QtWidgets.QAction(refresh_icon, "Refresh", self)
        self.refresh_button.triggered.connect(self.run_main_and_refresh)
        self.toolbar.addAction(self.refresh_button)

        # Set up the table
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Release Date", "Age Rating", "Notified At"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 12px;
                border: 1px solid #4c4c4c;
            }
            QHeaderView::section {
                background-color: #444444;
                color: #ffffff;
                padding: 5px;
                border: none;
            }
            QTableWidgetItem {
                padding: 10px;
            }
        """)

        # Add table to layout
        self.layout.addWidget(self.table)

        # Load initial data into the table
        self.load_data()

        # Set up a timer to run the main() function every hour
        self.start_background_task()

    def load_data(self):
        # Clear the table first
        self.table.setRowCount(0)

        # Connect to the database and fetch records
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT title, release_date, age_rating, notified_at FROM notified_releases")
        records = cursor.fetchall()

        # Populate the table with data
        for row_idx, row_data in enumerate(records):
            self.table.insertRow(row_idx)
            for col_idx, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)  # Make items non-editable
                self.table.setItem(row_idx, col_idx, item)

        # Close the database connection
        conn.close()

    def start_background_task(self):
        # Create a timer that triggers every hour
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_main_and_refresh)
        self.timer.start(3600000)  # 3600000 ms = 1 hour

    def run_main_and_refresh(self):
        main()          # Run the main function to fetch new data
        self.load_data()  # Refresh the GUI with the updated data

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Apply a darker theme to the application
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
        }
        QToolBar {
            background-color: #3b3b3b;
            border: none;
        }
        QPushButton, QToolButton {
            background-color: #4c8bf5;
            color: #ffffff;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton:hover, QToolButton:hover {
            background-color: #3c7be0;
        }
    """)

    window = MediaMonitoringGUI()
    window.show()
    sys.exit(app.exec_())
