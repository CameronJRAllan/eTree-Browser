from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Cantarell']
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
import numpy as np
import operator
import matplotlib.patheffects as path_effects

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
    weight : int
        The width of the figure to be created.
    height : int
        The height of the figure to be created.
    dpi : int
        The dots-per-inch for the figure typically 100.
    """

    # Create Figure instance (which stores our plots)
    self.fig = Figure(figsize=(2, 2), dpi=dpi, edgecolor='blue')

    # Add an initial plot to our figure
    self.canvasGraph = self.fig.add_subplot(111)

    # Fetch colour map
    self.colourMap = self.get_colour_map()

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
    self.setMinimumSize(self.size())

  def get_segment_colour_map(self, features):
    """
    Generates a colour map for segment features.

    Parameters
    ----------
    features : float[]
        Features information.

    Returns
    ----------
    newColourMap : str[]
        Colour map for each segment type.
    """

    hashList = {'1' : 'Grey',
                 '2':'Red',
                  '3':'Green',
                  '4':'greenyellow',
                  '5':'Pink',
                  '6':'Orange',
                  '7':'goldenrod',
                  '8':'indianred',
                  '9':'peachpuff',
                  '10':'deepskyblue',
                  '11':'firebrick',
                  '12':'orchid',
                  '13': 'moccasin',
                  '14':'slateblue',
                  '15':'turquoise',
                  '16':'tomato',
                  '17':'darkmagenta',
                  '18':'olivedrab'}
    # 'olive', 'lightsteelblue',
    # 'plum', 'mediumspringgreen',
    # 'lightsalmon', 'gold', 'burlywood']

    return hashList

  def plot_calma_data(self, loudnessValues, features, duration, type, **kwargs):
    """
    Takes CALMA data for a single track as input, and creates a plot.

    Parameters
    ----------
    loudnessValues : float[]
        An array of loudness / amplitude values.
    features : float[]
        Features information.
    duration : float
        The duration of the track.
    """

    # Replace colour map if needed
    if type == 'segment' : self.colourMap = self.get_segment_colour_map(features)
    if type == 'key' : self.colourMap = self.get_colour_map()

    # Hide placeholder text if visible
    try:
      self.placeHolderText.remove()
      text = self.fig.text(0.5, 0.65, kwargs['title'], horizontalalignment='center',
                    verticalalignment='center', fontsize=16)
      text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='white'),
                             path_effects.Normal()])

    except (KeyError, ValueError) as v:
      self.placeHolderText.set_text('')

    # Perform pre-processing
    nploudnessValues, duration, xSpaced, average = self.pre_processing(loudnessValues, duration)

    # Plot waveform
    self.canvasGraph.axes.cla()
    self.canvasGraph.plot(xSpaced, nploudnessValues)

    for index, key in enumerate(features):
      # Calculate graph positions
      lx, ly, rec = self.calculate_graph_element_position(features, key, index, duration, average)

      # Add annotation to plot
      self.canvasGraph.annotate(key[1], (lx, ly), weight='bold', color='Black',
                                fontsize=7, ha='center', va='center', rotation=270)
      self.ax.add_artist(rec)

    # Set axes labels
    self.ax.set_yticklabels([])
    self.ax.set_xlabel("Time (seconds)")

    # Add colour legend for keys
    keysAsSet = list(set([x[1] for x in features]))
    patches = []

    for k in keysAsSet:
      # Plot rectangle for key changes
      try:
        fc = self.colourMap[k]
      except KeyError as keyerr:
        fc = 'grey'

      patch = mpatch.Patch(color=fc, label=k)
      patches.append(patch)

    self.canvasGraph.legend(handles=patches, bbox_to_anchor=(1.00, 1), loc=2, borderaxespad=0, fontsize=7, ncol=2)
    self.fig.subplots_adjust(left=0.00, right=0.85, top=0.95)

    try:
      kwargs['release']
    except KeyError as v:
      # Causes crash with multiple plots
      self.finishDraw()

    self.fig.patch.set_alpha(1.0)
    return

  def calculate_graph_element_position(self, keyInfo, key, index, duration, average):
    # Rectangle takes (lowerleftpoint=(X, Y), width, height)
    xy = (float(key[0]), self.ax.get_ylim()[1])

    # If not the latest element in the key-change data
    if index < len(keyInfo) - 1:
      # Swap width and height as we are rotating 270 degrees
      height = keyInfo[index + 1][0] - keyInfo[index][0]
    else:
      height = duration - keyInfo[index][0]

    width = self.ax.get_ylim()[1]
    angle = 270

    # Plot rectangle for key changes
    try:
      fc = self.colourMap[key[1]]
    except KeyError as k:
      fc = 'grey'
    rec = mpatch.Rectangle(xy, width, height, angle=angle, alpha=0.5, fc=fc)

    # Calculate label positions
    rx, ry = rec.get_xy()
    lx = rx + rec.get_height() / 2.0
    ly = average

    return lx, ly, rec

  def get_colour_map(self):
    try:
      return {'C# minor' : 'Grey', 'A major' : 'Red', 'D minor' : 'Green',
                   'Eb Purple': 'greenyellow', 'D major' : 'Pink', 'G major' : 'Orange',
                   'G minor': 'goldenrod', 'A minor' : 'indianred', 'C minor' : 'peachpuff',
                   'B minor' : 'deepskyblue', 'Ab Major' : 'firebrick', 'Eb / D# minor' : 'orchid',
                   'Ab major' : 'moccasin', 'G# minor' : 'slateblue', 'Eb major' : 'turquoise',
                   'C major' : 'tomato', 'B major' : 'darkmagenta', 'F major' : 'olivedrab',
                   'F minor' : 'olive', 'Bb major' : 'lightsteelblue', 'Db major' : 'plum',
                   'Bb minor' : 'mediumspringgreen', 'E minor' : 'lightsalmon',
                   'F# / Gb major' : 'gold', 'F# minor' : 'burlywood'}

    # If colour not found to match, return grey as a last resort
    except KeyError as e:
      print('Unmatched colour: {0}'.format(e))
      return 'Grey'

  def pre_processing(self, loudnessValues, duration):
    # Clip
    loudnessValues = loudnessValues[100:-50]
    nploudnessValues = np.array(loudnessValues)

    # Frame-rate is the number of values provided, divided by the duration
    frame_rate = len(nploudnessValues) / duration

    # Calculate average for placing labels on Y-AXIS
    average = sum(loudnessValues) / len(loudnessValues)

    # Generate linear spacing for seconds in X-AXIS
    xSpaced = np.linspace(0, len(loudnessValues) / frame_rate, num=len(loudnessValues))

    return nploudnessValues, duration, xSpaced, average

  def finishDraw(self):
    self.fig.canvas.draw_idle()