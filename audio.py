import pyaudio
import subprocess
import numpy
import time
class Audio():
  def __init__(self, prog):
    self.pyAudio = pyaudio.PyAudio()  # PyAudio helps to reproduce raw data in pipe.
    self.is_playing = False
    self.currentUrl = None
    self.main = prog

  def ffmpeg_pipeline(self, url, **kwargs):
    # Save URL for future seeking
    self.currentUrl = url
    self.update_progress_signal = kwargs['update_track_progress']
    self.on_track_finished_signal = kwargs['track_finished']

    print('URL: ' + str(url))
    print('SEEK: ' + str(kwargs['seek']))

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
    self.is_playing = True
    byteCount = 0

    # While there is audio to play
    while self.is_playing and self.main.thread_flag:
      # Get raw audio chunk
      raw_audio_chunk = self.pipeline.stdout.read(44100 * 2)

      # Emit current time in seconds
      # 176400 is derived from 16-bit 44100Hz (88200 bytes), multiplied by 2 for stereo
      byteCount += 44100 * 2
      self.update_progress_signal.emit(seek + (byteCount // 176400))

      # Even an empty byte stream has length 3
      if len(str(raw_audio_chunk)) == 3:
        self.is_playing = False
      else:
        # Write to stream
        self.stream.write(raw_audio_chunk)

    if self.main.thread_flag:
      # Get next track
      self.stream.stop_stream()
      self.stream.close()
      self.pyAudio.terminate()
      self.on_track_finished_signal.emit()

  def get_url(self):
    return self.currentUrl

  def change_play_state(self):
    self.pyAudio = None
    if self.is_playing:
      self.stream.stop_stream()
    else:
      self.stream.start_stream()
    self.is_playing = not self.is_playing

  def set_volume(self, value):
    # If value is valid
    if (value <= 100) and (value >= 0):

      # Change system volume using PulseAudio
      subprocess.call(["amixer", "-D", "pulse", "sset", "Master", str(value) + "%"])

  def set_seek(self, seekTime):
    if self.currentUrl:
      # Format seek time as HH:MM:SS
      seekTime = time.strftime('%H:%M:%S', time.gmtime(seekTime))

      # Restart stream at this new time
      self.ffmpeg_pipeline(self.currentUrl, seek=seekTime)
