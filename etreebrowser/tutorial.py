from PyQt5 import QtCore, QtWidgets, QtGui

class Tutorial():
  def __init__(self, app):
    self.app = app

  def start_tutorial(self):
    # Move focus to browse page
    self.app.topMenuTabs.setCurrentIndex(1)

    self.stages = [["Browse list", self.app.browseList],
                   ["Playback Buttons", self.app.playPauseBtn],
                   ["Change browse type here", self.app.typeBrowseCombo],
                   ["Currently playing info", self.app.timeLbl]
                   ]

    self.pages = [self.stages]

    # Create first dialog window
    self.index = 0
    self.page = 0
    self.create_dialog(self.stages[self.index][0], self.stages[self.index][1])

    # Create graphics, e.g. arrows
    # self.create_arrow(1, 2, 100, 100)

  def create_dialog(self, text, widget):
    self.textDialog = QtWidgets.QMessageBox()
    self.textDialog.setText(text)
    self.textDialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    self.textDialog.setWindowOpacity(1)
    self.textDialog.buttonClicked.connect(self.next_stage)
    # self.textDialog.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    self.textDialog.setStyleSheet("""QMessageBox { background-color: (0, 0, 255, 50) };
                                      """) # #BA2024
    self.textDialog.move(widget.rect().center())
    self.textDialog.exec()

  def next_stage(self):
    # If reached end of this stage
    if self.index == len(self.stages) - 1:
      print('End of stage')
    else:
      self.index += 1
      print(self.index)
      self.create_dialog(self.stages[self.index][0], self.stages[self.index][1])

      # def create_arrow(self, x1, y1, x2, y2):
  #   self.arrow = QtWidgets.QGraphicsLineItem()
  #   self.arrow.setLine(x1, y1, x2, y2)