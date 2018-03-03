from PyQt5 import QtWidgets
import sys
import application

if __name__ == '__main__':
  # Create QApplication instance
  app = QtWidgets.QApplication(sys.argv)

  # Create dialog to show this instance
  dialog = QtWidgets.QMainWindow()

  # Start main event loop
  prog = application.mainWindow(dialog)

  # Show the main dialog window to user
  dialog.show()

  # On user exit, stop the application
  sys.exit(app.exec_())

