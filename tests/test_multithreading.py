import pytest
import multithreading

class TestMultithreading():
  @pytest.fixture(scope="function", autouse=True)
  def setup(self):
    self.errorSuccess = False
    self.threadFinished = False
    self.threadSuccess = False

  def threadFuncError(self, arg, **kwargs):
    raise(Exception)

  def threadFuncFinished(self, arg, **kwargs):
    self.threadFinished = True

  def threadFuncSuccess(self, arg, **kwargs):
    self.threadSuccess = True

  # def test_run_thread_error(self):
  #   with pytest.raises(Exception):
  #     assert(self.errorSuccess == False)
  #     self.WorkerThread = multithreading.WorkerThread(self.threadFuncError, None)
  #     self.WorkerThread.qtSignals.error.connect(self.threadFuncError)
  #     self.WorkerThread.run()

  def test_run_thread_success(self):
    assert(self.threadSuccess == False)
    self.WorkerThread = multithreading.WorkerThread(self.threadFuncSuccess, None)
    self.WorkerThread.qtSignals.error.connect(self.threadFuncError)
    self.WorkerThread.run()
    assert(self.threadSuccess == True)

  def test_run_thread_finished(self):
    assert(self.threadFinished == False)
    self.WorkerThread = multithreading.WorkerThread(self.threadFuncFinished, None)
    self.WorkerThread.qtSignals.error.connect(self.threadFuncError)
    self.WorkerThread.run()
    assert(self.threadFinished == True)