try:
  from PyQt5 import QtWidgets, QtGui
  import sys
  import application
  import platform
except (ImportError, ModuleNotFoundError) as e:
  print('You are missing package: ' + str(e)[15:])
  print('Quitting ..')
  exit(1)

# Create QApplication instance
app = QtWidgets.QApplication(sys.argv)

# If using Windows, set some font and theme properties
if platform.system() == 'Windows':
  app.setStyle("Fusion")
  font = QtGui.QFont("Cantarell", 10)
  app.setFont(font)

# Create dialog to show this instance
dialog = QtWidgets.QMainWindow()

# Start main event loop
prog = application.mainWindow(dialog)

# Show the main dialog window to user
dialog.show()

# On user exit, stop the application
sys.exit(app.exec_())

