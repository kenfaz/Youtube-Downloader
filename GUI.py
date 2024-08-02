from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
import sys

xp, yp, width, height = 1420, 300, 800, 500

# TODO: Add the labels to display events.
# TODO: Format the data retrieved.

# events = main()  # Retrieve the calendar events

def window():
    # Import font
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(xp, yp, width, height)
    win.setFixedSize(width, height)
    win.setWindowTitle("YouTube Downloader")
    win.show()
    sys.exit(app.exec_())


window()