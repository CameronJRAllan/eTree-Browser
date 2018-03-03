from PyQt5 import QtCore
import traceback
import sys

class WorkerThreadSignals(QtCore.QObject):
  '''
    This blog post from Maya Posch was very useful in developing
    understanding of thread behaviour in Qt:
    https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/

    Defines the signals available from a running worker thread
    allowing communication between theads. To declare signals
    we must sub-class QObject.

    There are several bespoke signals, but the ones available
    for all functions executed are:

    finished
        The function has finished with no error raised.

    error
        A tuple containing the execution type, the value,
        and a trace-back of the error raised.

    result
        Returns an object representing the result of the
        function executed.

    progress
        An integer value, used to updated progress, for
        example in a progress bar.

    '''

  # Generic signals, used by many components
  finished = QtCore.pyqtSignal()
  error = QtCore.pyqtSignal(tuple)
  result = QtCore.pyqtSignal(object)
  progress = QtCore.pyqtSignal(int)

  # Map interface
  js_callback = QtCore.pyqtSignal(str, str, str)
  homepage_end = QtCore.pyqtSignal()
  homepage_start = QtCore.pyqtSignal()

  # Table interface
  add_table_item = QtCore.pyqtSignal(int, int, object)
  update_table_item  = QtCore.pyqtSignal(int, int, str)
  start_table = QtCore.pyqtSignal(int, int, list)
  end_table = QtCore.pyqtSignal()

  # Audio handler
  update_track_progress = QtCore.pyqtSignal(float)
  track_finished = QtCore.pyqtSignal()
  update_track_duration = QtCore.pyqtSignal(int)
  scrobble_track = QtCore.pyqtSignal()

  # CALMA
  finished_set_new_track = QtCore.pyqtSignal(object, object, object, float, dict)

class WorkerThread(QtCore.QRunnable):
  '''
    A class for defining a worker thread.

    We inherit properties from QRunnable to in order to handle operations such as thread setup, signals and wrap-up.

    We sub-class worker from QtCore.QRunnable, in order to gain access to various public function we will require.
  '''

  def __init__(self, function, *args, **kwargs):
    '''
      A constructor for creating a new worker thread

      The constuctor for the Worker class primarily sets up signals for this particular worker, which will be
      required during process or if an error occurs.

      Parameters
      ----------
      fn : function
        The function to be executed within the worker.

      args : list
        A list of arguments.

      kwargs : list
        A list of keyword arguments.
    '''

    # Run constructor of parent class
    super(WorkerThread, self).__init__()

    # Store constructor arguments as instance variables for later retrieval and use
    self.func = function
    self.arguments = args
    self.k_arguments = kwargs
    self.qt_signals = WorkerThreadSignals()

    # Add the callback to our kwargs
    kwargs['js_callback'] = self.qt_signals.js_callback
    kwargs['homepage_end'] = self.qt_signals.homepage_end
    kwargs['homepage_start'] = self.qt_signals.homepage_start
    kwargs['add_table_item'] = self.qt_signals.add_table_item
    kwargs['update_table_item'] = self.qt_signals.update_table_item
    kwargs['start_table_callback'] = self.qt_signals.start_table
    kwargs['fin_table_callback'] = self.qt_signals.end_table
    kwargs['track_finished'] = self.qt_signals.track_finished
    kwargs['update_track_progress'] = self.qt_signals.update_track_progress
    kwargs['update_track_duration'] = self.qt_signals.update_track_duration
    kwargs['scrobble_track'] = self.qt_signals.scrobble_track
    kwargs['finished'] = self.qt_signals.finished
    kwargs['finished_set_new_track'] = self.qt_signals.finished_set_new_track

  @QtCore.pyqtSlot()
  def run(self):
    '''
      Starts the execution of a thread, with the set function of the
      class, and any set keyword / positional arguments.

      Retrieve the arguments and keyword arguments 'kwargs' and use them to start processing, sending signals when
      required
    '''

    # Try executing the thread
    try:
      thread_returned_value = self.func(*self.arguments, **self.k_arguments)
    # If an error occurs, return this to the main thread
    except:
      # Print the traceback of the error that occured
      traceback.print_exc()
      executionType, errorValue = sys.exc_info()[:2]

      # Emit the error so that main program is made aware
      self.qt_signals.error.emit((executionType, errorValue, traceback.format_exc()))
    # If no error raised, return the result
    else:
      # Return the result of the processing
      self.qt_signals.result.emit(thread_returned_value)
    # At the end, return a finished signal
    finally:
      # Tell main program that this thread has finished
      self.qt_signals.finished.emit()
