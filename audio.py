import pyaudio
import subprocess
import time
import multithreading
import qtawesome as qta
from random import randint
import sys
class Audio():
  def __init__(self, app):
    self.app = app
    self.isPlaying = False
    self.threadFlag = True
    self.currentUrl = None

    # Set-up volume controls
    self.app.volumeSlider.setValue(50)
    self.app.volumeSlider.valueChanged.connect(self.set_volume)

    # Set icons for playback
    self.app.playPauseBtn.setIcon(qta.icon('fa.play'))
    self.app.prevBtn.setIcon(qta.icon('fa.step-backward'))
    self.app.nextBtn.setIcon(qta.icon('fa.step-forward'))
    self.app.lastfmBtn.setIcon(qta.icon('fa.lastfm'))

  def ffmpeg_pipeline(self, url, **kwargs):
    self.pyAudio = pyaudio.PyAudio()  # PyAudio helps to reproduce raw data in pipe.

    # Save URL for future seeking
    self.currentUrl = url
    self.update_progress_signal = kwargs['update_track_progress']
    self.on_track_finished_signal = kwargs['track_finished']
    self.scrobble_track = kwargs['scrobble_track']

    # Get duration of track
    duration = subprocess.check_output(['ffprobe', '-i', url, '-show_entries', 'format=duration', '-v', 'quiet',
                                        '-of', 'csv=%s' % ("p=0")])
    duration = str(duration).replace("b'", '').replace("\\n'", '')
    kwargs["update_track_duration"].emit(float(duration))

    # Create ffMPEG command, options chosen from sub-set of list given by 'ffmpeg -formats'
    command = ['ffmpeg',
               '-ss', str(kwargs['seek']),  # Set start time to that provided
               '-i', url,  # Set input to URL provided
               '-loglevel', 'error',
               '-f', 's16le',  # PCM signed 16-bit little-endian
               '-acodec', 'pcm_s16le',  # PCM is used to get raw audio data
               '-ar', '44100',  # Set sampling frequency to most common
               '-ac', '2',  # 2 channels for stereo
               '-']

    # Create pipe-line
    self.pipeline = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10 ** 8)

    # Set pipe-line destination to pyAudio instance
    self.stream = self.pyAudio.open(format=pyaudio.paInt16,
                                    channels=2,
                                    rate=44100,
                                    output=True)

    # Start pipe-line process
    if not kwargs['seek']:
      self.start_audio(0)
    else:
      self.start_audio(kwargs['seek'])

  def start_audio(self, seek):
    self.isPlaying = True
    self.hasScrobbled = False
    byteCount = 0

    # While there is audio to play
    while self.isPlaying and self.threadFlag:
      # Get raw audio chunk
      raw_audio_chunk = self.pipeline.stdout.read(44100 * 2)

      # Emit current time in seconds
      # 176400 is derived from 16-bit 44100Hz (88200 bytes), multiplied by 2 for stereo
      byteCount += 44100 * 2
      self.update_progress_signal.emit(seek + (byteCount // 176400))
      if (byteCount // 176400) > 30 and not self.hasScrobbled:
        self.hasScrobbled = True
        self.scrobble_track.emit()
      # Even an empty byte stream has length 3
      if len(str(raw_audio_chunk)) == 3:
        self.isPlaying = False
      else:
        # Write to stream
        self.stream.write(raw_audio_chunk)

    # Get next track
    self.stream.stop_stream()
    self.stream.close()
    self.stream = None
    self.pipeline = None
    self.pyAudio.terminate()

    if not self.isPlaying:
      self.on_track_finished_signal.emit()

    return

  def get_url(self):
    return self.currentUrl

  def change_play_state(self):
    self.pyAudio = None

    try:
      if self.isPlaying:
        self.stream.stop_stream()
      else:
        self.stream.start_stream()
      self.isPlaying = not self.isPlaying
    except AttributeError as e:
      print('self.Stream not set')

  def set_volume(self, value):
    # If value is valid
    if (value <= 100) and (value >= 0):

      # Change system volume using PulseAudio
      subprocess.call(["amixer", "-D", "pulse", "sset", "Master", str(value) + "%"])

      return True
    else:
      return False

  def set_seek(self, seekTime):
    if self.currentUrl:
      # Format seek time as HH:MM:SS
      seekTime = time.strftime('%H:%M:%S', time.gmtime(seekTime))

      # Restart stream at this new time
      self.ffmpeg_pipeline(self.currentUrl, seek=seekTime)
    else:
      return False

  def next_click(self):
    self.fetch_next_track()
    # self.start_audio_thread(self.playlist[self.playlist_index][0], 0)

  def previous_click(self):
    # Fetch_next_track increments by one, so we decrement by two
    self.playlist_index -= 2
    if self.playlist_index < -1 : self.playlist_index = -1
    self.fetch_next_track()
    #self.start_audio_thread(self.playlist[self.playlist_index][0], 0)

  def fetch_next_track(self):
    self.kill_audio_thread()
    time.sleep(1)

    if self.app.repeatCombo.currentText() == 'Repeat All':
      if self.playlist_index <= len(self.playlist) - 1:
        self.playlist_index += 1
      else:
        self.playlist_index = 0
    self.app.trackLbl.setText(self.playlist[self.playlist_index][1])
    if self.app.repeatCombo.currentText() == 'Shuffle':
      self.playlist_index = randint(0, len(self.playlist))

    self.app.trackLbl.setText(self.playlist[self.playlist_index][1])
    # Start playing next track in playlist
    self.start_audio_thread(self.playlist[self.playlist_index][0], 0)

  def send_duration(self, duration):
    # Update duration of progress bar
    self.app.trackProgress.setMaximum(duration)
    self.duration = duration

  def start_audio_thread(self, url, seek):
    self.kill_audio_thread()
    worker = multithreading.WorkerThread(self.app.audioHandler.ffmpeg_pipeline, url, seek=seek)
    worker.qt_signals.track_finished.connect(self.fetch_next_track)
    worker.qt_signals.update_track_progress.connect(self.update_seekbar)
    worker.qt_signals.update_track_duration.connect(self.send_duration)
    worker.qt_signals.scrobble_track.connect(self.app.scrobble_track_lastfm)
    self.app.audioThreadpool.start(worker)

  def update_seekbar(self, timestamp):
    """
    Updates the seekbar with the current progress of the track playing

    Parameters
    ----------
    self : instance
        Class instance.
    timestamp : str
        Timestamp provided by FFMPEG.
    """

    # Calculate minutes and seconds format
    self.app.trackProgress.setValue(round(float(timestamp)))
    m, s = divmod(round(float(timestamp)), 60)
    dm, ds = divmod(round(float(self.duration)), 60)

    # Ensures that when the seconds is < 10, we add an extra 0 to ensure correct formatting
    if s < 10:
      s = '0' + str(s)
    if ds < 10:
      ds = '0' + str(ds)
    lbl = str(m) + ':' + str(s) + ' / ' + str(dm) + ':' + str(ds)

    # Add key information if applicable
    if self.hasCalma:
      lbl = lbl + ' (' + str(self.calmaHandler.get_key_at_time(timestamp)) + ')'

    # Set time label to new time
    self.app.timeLbl.setText(lbl)

  def kill_audio_thread(self):
    # Tell thread to stop
    self.threadFlag = False

    # Wait until thread can respond to our flag change
    time.sleep(0.5)

    # Reset flag
    self.threadFlag = True

  def user_audio_clicked(self, audioList, index):
    self.playlist = []
    self.playlist_index = 0

    # Add to playlist
    first = True
    num = -1
    for track in audioList:
      num += 1
      self.playlist.append([track['audio']['value'], track['label']['value']])
      if first and num >= index:
        first = False
        self.playlist_index = num
        self.start_audio_thread(track['audio']['value'], 0)

        # self.append_history(track)

        self.app.trackLbl.setText(track['label']['value'])

        # Check whether calma data available
        if self.app.calmaHandler.get_features_track(track['audio']['value']):
          self.hasCalma = True
        else:
          self.hasCalma = False

          # If adding tracks after to the queue
          # else:
          #   if num >= index:
          #     self.playlist.append([track['audio']['value'], track['label']['value']])

    self.isPlaying = True
    self.app.playPauseBtn.setIcon(qta.icon('fa.pause'))
    self.app.nowPlayingHandler.update_playlist_view()

  def extract_tracklist_single_format(self, tracklist):
    audioList = []
    found = False
    foundFormat = ''
    for format in self.app.formats:
      # Look at each track
      for track in tracklist['results']['bindings']:
        # If we have not found a format yet
        if found is False:
          # If we find a suitable format
          if track['audio']['value'].lower().endswith(format):
            # Store and ensure we don't continue checking
            found = True
            foundFormat = format
            self.app.debugDialog.add_line('{0}: found matching format {1}'.format(sys._getframe().f_code.co_name, foundFormat))
    if not found:
      foundFormat = '.flac'
      self.app.debugDialog.add_line('{0}: issue finding format, defaulting to {1}'.format(sys._getframe().f_code.co_name, foundFormat))

    num = 0
    for track in tracklist['results']['bindings']:
      # If we find a track with a suitable file extension
      if foundFormat in track['audio']['value'][-7:]:
        audioList.append(track)
        num += 1

    return audioList

  def play_pause(self):
    # If we're currently playing a track
    if self.isPlaying:
      self.kill_audio_thread()
      time.sleep(0.5)
      self.app.playPauseBtn.setIcon(qta.icon('fa.play'))
    else:
      # Start playing audio from position
      self.start_audio_thread(self.playlist[self.playlist_index][0], self.app.trackProgress.value())
      self.app.playPauseBtn.setIcon(qta.icon('fa.pause'))
    self.isPlaying = not self.isPlaying

  def track_seek(self):
    """
    Starts a given track at a particular seek time.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    self.start_audio_thread(self.get_url(), self.app.trackProgress.value())
