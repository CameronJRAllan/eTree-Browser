from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
import numpy as np

class CalmaPlot(FigureCanvas):
  """
  This class provides functionality for providing graphical representations of CALMA data.
  """
  def __init__(self, width, height, dpi, hasCalma, parent=None):
    """
    Constructs an instance of the CALMA graphing class.

    An instance of CalmaPlot inherits FigureClass, a MatPlotLib class for displaying plots in the
    text of a PyQt5 application. It generates a figure (upon which we may draw), as well as a canvas to
    place the figure upon.

    Parameters
    ----------
    self : instance
        Class instance.
    weight : int
        The width of the figure to be created.
    height : int
        The height of the figure to be created.
    dpi : int
        The dots-per-inch for the figure typically 100.
    """

    # Create Figure instance (which stores our plots)
    self.fig = Figure(figsize=(width, height), dpi=dpi, edgecolor='blue')

    # Add an initial plot to our figure
    self.canvasGraph = self.fig.add_subplot(111)

    # Initialize figure canvas, which initializes an instance of QtWidget
    FigureCanvas.__init__(self, self.fig)
    self.setParent(parent)

    # Store reference to axes
    self.ax = self.fig.gca()

    # Hide tick labels to create default style
    self.ax.set_yticklabels([])
    self.ax.set_xticklabels([])

    # Add placeholder text
    if hasCalma:
      self.placeHolderText = self.fig.text(0.5, 0.65,'Click on a performance track for CALMA data',horizontalalignment='center',
                                           verticalalignment='center', fontsize=16)
    else:
      self.placeHolderText = self.fig.text(0.5, 0.65,'No CALMA data available for this query',horizontalalignment='center',
                                           verticalalignment='center',
                                           fontsize=16)

    # Make background transparent
    self.fig.patch.set_alpha(1.0)

    # Resize with window
    FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

  def plot_calma_data(self, loudnessValues, keyInfo, duration):
    """
    Takes CALMA data for a single track as input, and creates a plot.

    Parameters
    ----------
    self : instance
        Class instance.
    loudnessValues : float[]
        An array of loudness / amplitude values.
    keyInfo : float[]
        Key change information.
    duration : float
        The duration of the track.
    """

    # Hide placeholder text if visible
    self.placeHolderText.set_text('')

    # Clip
    loudnessValues = loudnessValues[100:-50]
    nploudnessValues = np.array(loudnessValues)

    # Frame-rate is the number of values provided, divided by the duration
    frame_rate = len(nploudnessValues) / duration

    # Calculate average for placing labels on Y-AXIS
    average = sum(loudnessValues) / len(loudnessValues)

    # Generate linear spacing for seconds in X-AXIS
    xSpaced = np.linspace(0, len(loudnessValues) / frame_rate, num=len(loudnessValues))

    # Plot waveform
    self.canvasGraph.axes.cla()
    self.canvasGraph.plot(xSpaced, nploudnessValues)
    colourMap = {'C# minor' : 'Grey', 'A major' : 'Red', 'D minor' : 'Green',
                 'Eb Purple': 'greenyellow', 'D major' : 'Pink', 'G major' : 'Orange',
                 'G minor': 'goldenrod', 'A minor' : 'indianred', 'C minor' : 'peachpuff',
                 'B minor' : 'deepskyblue', 'Ab Major' : 'firebrick', 'Eb / D# minor' : 'orchid',
                 'Ab major' : 'moccasin', 'G# minor' : 'slateblue', 'Eb major' : 'turquoise',
                 'C major' : 'tomato', 'B major' : 'darkmagenta', 'F major' : 'olivedrab',
                 'F minor' : 'olive', 'Bb major' : 'lightsteelblue', 'Db major' : 'plum',
                 'Bb minor' : 'mediumspringgreen', 'E minor' : 'lightsalmon',
                 'F# / Gb major' : 'gold'}

    for index, key in enumerate(keyInfo):
      # Rectangle takes (lowerleftpoint=(X, Y), width, height)
      xy = (float(key[0]), self.ax.get_ylim()[1])

      # If not the latest element in the key-change data
      if index < len(keyInfo) - 1:
        # Swap width and height as we are rotating 270 degrees
        height = keyInfo[index+1][0] - keyInfo[index][0]
      else:
        height = duration - keyInfo[index][0]

      width = self.ax.get_ylim()[1]
      angle = 270

      # Plot rectangles for key changes
      rec = mpatch.Rectangle(xy, width, height, angle=angle, alpha=0.5, fc=colourMap[key[1]])
      self.ax.add_artist(rec)

      # Calculate label positions
      rx, ry = rec.get_xy()
      lx = rx + rec.get_height() / 2.0
      ly = average

      # Add annotation to plot
      self.canvasGraph.annotate(key[1], (lx, ly), weight='bold', color='Black',
                                fontsize=7, ha='center', va='center', rotation=270)

    # Set axes labels
    self.ax.set_yticklabels([])
    self.ax.set_xlabel("Time (seconds)")

    # Add colour legend for keys
    keysAsSet = list(set([x[1] for x in keyInfo]))
    patches = []

    for k in keysAsSet:
      patch = mpatch.Patch(color=colourMap[k], label=k)
      patches.append(patch)
    self.canvasGraph.legend(handles=patches, bbox_to_anchor=(1.00, 1), loc=2, borderaxespad=0, fontsize=7)
    self.fig.subplots_adjust(left=0.01, right=0.9, top=0.7, bottom=0.3)

    self.draw()
    self.fig.patch.set_alpha(1.0)

    print('Finished graph plot func')
    return

