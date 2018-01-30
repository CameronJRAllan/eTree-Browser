import pyaudio
import subprocess
import time
import multithreading
import qtawesome as qta
from random import randint
import sys
class Audio():
  """
  The audio class handles playback of audio links stored within the eTree meta-data set.

  It primarily utilizes FFMPEG to handle the decoding of the audio into a byte-stream,
  which may then be piped into a PyAudio instance and played to the user, all within a
  seperate thread from the main application thread loop.
  """
  def __init__(self, app):
    """
    Creates an instance of the Audio class for handling audio-related operations.

    Parameters
    ----------
    self : instance
        Class instance.
    app : instance
        Main dialog reference.
    """

    self.app = app
    self.isPlaying = False
    self.threadFlag = True
    self.currentUrl = None
    self.hasCalma = False
    self.userDragging = False

  def ffmpeg_pipeline(self, url, **kwargs):
    """
    Creates an FFMPEG sub-process to handling audio decoding,
    while emitting relevant meta-data to the main application thread
    as necessary.

    Parameters
    ----------
    self : instance
        Class instance.
    url : str
        The URL of the audio link we wish to play.
    kwargs : {}
        Dictionary of signals which emit to the main application thread.
    """

    # If testing, set flag
    if 'test' in kwargs:
      self.test = True
    else:
      self.test = False

    # Create PyAudio instance
    self.pyAudio = pyaudio.PyAudio()

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
    """
    Starts the process is reading the sub-process (FFMPEG) audio byte
    stream into PyAudio for playback.

    Parameters
    ----------
    self : instance
        Class instance.
    seek : int
        The position we wish to began at (where the start is 0).
    """

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

        # If testing, exit loop
        if self.test == True:
          self.threadFlag = False

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
    """
    Returns the currently set URL.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    return self.currentUrl

  def change_play_state(self):
    """
    Either starts of resumes playback of the currently set track URL.

    Parameters
    ----------
    self : instance
        Class instance.
    """

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
    """
    Sets the volume of the application.

    Parameters
    ----------
    self : instance
        Class instance.
    value : int
        The value (in range 0 to 100) that we wish to set volume to.
    """

    # If value is valid
    if (value <= 100) and (value >= 0):

      # Change system volume using PulseAudio
      subprocess.call(["amixer", "-D", "pulse", "sset", "Master", str(value) + "%"])

      return True
    else:
      return False

  def set_seek(self, seekTime):
    """
    Sets the current position we are playing back, in the track.

    Parameters
    ----------
    self : instance
        Class instance.
    seekTime : int
        The time we wish to seek to.
    """

    if self.currentUrl:
      # Format seek time as HH:MM:SS
      seekTime = time.strftime('%H:%M:%S', time.gmtime(seekTime))

      # Restart stream at this new time
      self.ffmpeg_pipeline(self.currentUrl, seek=seekTime)
    else:
      return False

  def next_click(self):
    """
    Goes to the next track.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    self.fetch_next_track()
    self.app.playPauseBtn.setIcon(qta.icon('fa.pause'))

  def previous_click(self):
    """
    Goes to the previous track.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    # Fetch_next_track increments by one, so we decrement by two
    self.playlist_index -= 2

    if self.playlist_index < -1 : self.playlist_index = -1

    self.fetch_next_track()
    self.app.playPauseBtn.setIcon(qta.icon('fa.pause'))

  def fetch_next_track(self):
    """
    Fetches the next track to be played, depending on user preferences for
    playback behaviour in the queue.

    Parameters
    ----------
    self : instance
        Class instance.
    """

    self.kill_audio_thread()
    time.sleep(1)

    self.playlist_index = self.get_next_track_index()

    self.app.trackLbl.setText(self.playlist[self.playlist_index][1].title())

    # Start playing next track in playlist
    self.start_audio_thread(self.playlist[self.playlist_index][0], 0)

  def get_next_track_index(self):
    if self.app.repeatCombo.currentText() == 'Repeat All':
      if self.playlist_index <= len(self.playlist) - 1:
        self.playlist_index += 1
      else:
        self.playlist_index = 0

    if self.app.repeatCombo.currentText() == 'Shuffle':
      self.playlist_index = randint(0, len(self.playlist))

    return self.playlist_index

  def send_duration(self, duration):
    # Update duration of progress bar
    self.app.trackProgress.setMaximum(duration)
    self.duration = duration

  def start_audio_thread(self, url, seek, **kwargs):
    self.kill_audio_thread()
    worker = multithreading.WorkerThread(self.app.audioHandler.ffmpeg_pipeline, url, seek=seek)
    worker.qt_signals.track_finished.connect(self.fetch_next_track)
    worker.qt_signals.update_track_progress.connect(self.update_seekbar)
    worker.qt_signals.update_track_duration.connect(self.send_duration)
    worker.qt_signals.scrobble_track.connect(self.app.scrobble_track_lastfm)

    if 'testing' not in kwargs : self.app.audioThreadpool.start(worker)

  def start_audio_single_link(self, url, seek, **kwargs):
    self.playlist = [[url, 'Track Name']]
    self.playlist_index = 0
    self.app.trackLbl.setText(self.playlist[0][1].title())
    self.isPlaying = True
    self.app.playPauseBtn.setIcon(qta.icon('fa.pause'))

    if 'testing' not in kwargs : self.start_audio_thread(url, seek)

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
    if not self.userDragging:
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
      lbl = lbl + ' (' + str(self.app.calmaHandler.get_key_at_time(timestamp)) + ')'

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
    """
    Starts audio playback when a user clicks on a release, or track.

    Parameters
    ----------
    self : instance
        Class instance.
    audioList : []
        A list, where each element is a dictionary with information regarding 1 track.
    index : int
        The index in the playlist we wish to begin from.
    """

    self.playlist = []
    self.playlist_index = 0

    # Add to playlist
    first = True
    num = 0
    for track in audioList:
      self.playlist.append([track['audio']['value'], track['label']['value'], track['tracklist']['value']])
      if first:
        first = False
        self.playlist_index = num
        self.start_audio_thread(track['audio']['value'], 0)

        self.app.append_history_table(track['label']['value'],
                                      self.app.sparql.get_artist_from_tracklist(track['tracklist']['value']),
                                      self.app.sparql.get_label_tracklist(track['tracklist']['value']),
                                      track['audio']['value'])

        self.app.trackLbl.setText(track['label']['value'].title())

        # Check whether calma data available
        if self.app.calmaHandler.get_features_track(track['audio']['value']):
          self.hasCalma = True
        else:
          self.hasCalma = False

    self.isPlaying = True
    self.app.playPauseBtn.setIcon(qta.icon('fa.pause'))
    self.app.nowPlayingHandler.update_playlist_view()

  def extract_tracklist_single_format(self, tracklist):
    """
    Takes an input a tracklist dictionary, and extracts a distinct tracklist
    relating to a single, user-preferred, format.

    Parameters
    ----------
    self : instance
        Class instance.
    tracklist : dict
        Dictionary of tracks for a particular release.
    """

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

  def lock_progress_user_drag(self):
    self.userDragging = True

  def track_seek(self):
    """
    Starts a given track at a particular seek time.

    Parameters
    ----------
    self : instance
        Class instance.
    """
    self.userDragging = False
    self.start_audio_thread(self.get_url(), self.app.trackProgress.value())
