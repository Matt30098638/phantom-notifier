# gui.py
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import sqlite3
from main import main  # Import the main function

DB_NAME = 'media_monitoring.db'

class MediaMonitoringGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Monitoring Suggestions")
        self.setGeometry(300, 200, 700, 400)

        # Set up the table
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Release Date", "Age Rating", "Notified At"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Set layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

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
                self.table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(col_data)))

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
    window = MediaMonitoringGUI()
    window.show()
    sys.exit(app.exec_())
