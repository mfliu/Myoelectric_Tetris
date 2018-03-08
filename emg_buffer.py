'''Interface to the BYB SpikerBox through HIDAPI'''
import hid

# Constants
SIZE_OF_CIRC_BUFFER = 4024
SIZE_OF_MESSAGES_BUFFER = 64
ESCAPE_SEQUENCE_LENGTH = 6

BUFFER_SIZE = 65
BYB_VID = 0x2e73
BYB_PID_MUSCLE_SB_PRO = 0x1
BYB_PID_NEURON_SB_PRO = 0x2

SIZE_OF_MAIN_CIRCULAR_BUFFER = 40000
BOARD_WITH_ADDITIONAL_INPUTS = 1

ESCAPE_SEQUENCE = {'start': [255, 255, 1, 1, 128, 255], 'end': [255, 255, 1, 1, 129, 255]}


class SpikerBox(object):
  '''A wrapper around HIDAPI to handle the BYB device'''

  def __init__(self):
    self.device = None

    self.circ_buffer = [0] * SIZE_OF_CIRC_BUFFER
    self.cbuf_head = 0
    self.cbuf_tail = 0
    self.circ_buffer[0] = ord('\n')

    self.inside_escape = False
    self.escape_index = 0

    self.num_channels = 2
    self.sampling_rate = 10000

  def open_device(self):
    '''Open the device if it isn't already open. Returns a message indicating success or the reason
    for failure'''
    if self.device:
      return 'Device already open'

    self.device = hid.device()
    try:
      self.device.open(BYB_VID, BYB_PID_MUSCLE_SB_PRO)
    except ValueError as exp:
      return 'Value error: {}'.format(exp)
    except MemoryError as exp:
      return 'Memory error: {}'.format(exp)
    except IOError as exp:
      return 'IO error: {}'.format(exp)

    print(self.ask_for_capabilities())
    print(self.ask_for_maximum_ratings())
    print(self.start_device())
    print(self.ask_for_board())
    return 'Opened device'

  def send_req(self, req_str):
    '''Utility method to send a request string'''
    #print(req_str)
    req_bytes = list(map(ord, req_str))
    #print(req_bytes)
    buff = [0] * 64
    buff[0] = 0x3f
    buff[1] = 62
    
    for i in range(0, len(req_bytes)):
      buff[i + 2] = req_bytes[i]
    #write_res = self.device.write(list(map(ord, req_str)))
    write_res = self.device.write(buff)
    return write_res >= 0

  def ask_for_capabilities(self):
    '''Ask microcontroller for its capabilities'''
    if not self.device:
      return 'Device is not open'

    if self.send_req('?:;\n'):
      return 'Asked for capabilities'

    return 'Asking for capabilities failed due to write error: {}'.format(self.device.error())

  def ask_for_maximum_ratings(self):
    '''Ask microcontroller for maximum ratings'''
    if not self.device:
      return 'Device is not open'

    if self.send_req('max:;\n'):
      return 'Asked for maximum ratings'

    return 'Asking for maximum ratings failed due to write error: {}'.format(self.device.error())

  def start_device(self):
    '''Send the start command'''
    if not self.device:
      return 'Device is not open'

    if self.send_req('start:;\n'):
      return 'Started device'

    return 'Starting device failed due to write error: {}'.format(self.device.error())

  def ask_for_board(self):
    '''Ask if we have add on boards connected'''
    if not self.device:
      return 'Device is not open'

    if self.send_req('board:;\n'):
      return 'Asked for add on boards'

    return 'Asking for add on boards failed due to write error: {}'.format(self.device.error())

  def read_buffer(self):
    '''Read one raw_buffer of data from the device. Returns a string indicating success or the
    reason for failure and the raw_buffer as a list'''
    if not self.device:
      return 'Device is not open', []

    raw_buffer = 0
    try:
      raw_buffer = self.device.read(256, 100)
    except ValueError as exp:
      return 'Value error: {}'.format(exp), []
    except IOError as exp:
      return 'IO error: {}'.format(exp), []

    #print(raw_buffer)
    if not raw_buffer:
      return self.device.error()  + ' Read zero bytes!', []

    package_size = raw_buffer[1] & 0xFF
    for i in range(2, package_size + 2):
      self.detect_escape(raw_buffer[i])
      if not self.inside_escape:
        self.circ_buffer[self.cbuf_head] = raw_buffer[i]
        self.cbuf_head += 1
        if self.cbuf_head >= len(self.circ_buffer):
          self.cbuf_head = 0

    # NOTE: I think not explicitly making sure these are unsigned will be OK, but I'm not certain.
    # It may depend on the values read by the sensor
    msb = 0
    lsb = 0
    have_data = True
    out_buffer = []
    frame_count = 0
    while have_data:
      msb = self.circ_buffer[self.cbuf_tail] & 0xFF
      if msb > 127:
        if self.check_full_frame() and len(out_buffer) < 1000:
          frame_count += 1
          for i in range(self.num_channels):
            msb = self.circ_buffer[self.cbuf_tail] & 0x7F
            self.cbuf_tail += 1
            if self.cbuf_tail >= len(self.circ_buffer):
              self.cbuf_tail = 0

            lsb = self.circ_buffer[self.cbuf_tail] & 0xFF

            # Test for errors
            if lsb > 127:
              frame_count -= 1
              break

            lsb = self.circ_buffer[self.cbuf_tail] & 0x7F
            msb = msb << 7
            val = lsb | msb
            # NOTE: These are magic numbers that I just copied from the C++
            out_buffer.append((val - 512) * 62)
            if self.check_end_frame() or len(out_buffer) > 1000:
              break
            self.cbuf_tail += 1
            if self.cbuf_tail >= len(self.circ_buffer):
              self.cbuf_tail = 0
        else:
          have_data = False
          break
      if not have_data:
        break

      self.cbuf_tail += 1
      if self.cbuf_tail >= len(self.circ_buffer):
        self.cbuf_tail = 0

      if self.cbuf_tail == self.cbuf_head:
        have_data = False
        break

    return 'Read {} frames'.format(frame_count), out_buffer

  def check_end_frame(self):
    '''Checks to see if we're at the end of a frame'''
    tail = self.cbuf_tail + 1
    if tail >= len(self.circ_buffer):
      tail = 0

    next_byte = self.circ_buffer[tail] & 0xFF
    return next_byte > 127

  def check_full_frame(self):
    '''Checks to see if there's at least one full frame in the buffer'''
    tail = self.cbuf_tail + 1
    if tail >= len(self.circ_buffer):
      tail = 0

    while tail != self.cbuf_head:
      next_byte = self.circ_buffer[tail] & 0xFF
      if next_byte > 127:
        return True

      tail += 1
      if tail >= len(self.circ_buffer):
        tail = 0

  def detect_escape(self, new_byte):
    '''Detect if we are reading an escape sequence'''
    seq = ESCAPE_SEQUENCE['end'] if self.inside_escape else ESCAPE_SEQUENCE['start']
    if seq[self.escape_index] == new_byte:
      self.escape_index += 1
      if self.escape_index == len(seq):
        if not self.inside_escape:
          # Rewind buffer head to ignore escape bytes
          # The -1 is because we check this before adding the byte to the circular buffer
          self.cbuf_head -= len(seq) - 1
          if self.cbuf_head < 0:
            self.cbuf_head += len(self.circ_buffer)
        self.inside_escape = not self.inside_escape
        self.escape_index = 0
    else:
      self.escape_index = 0

  def close_device(self):
    '''Close the device if it isn't already closed. Returns an int signaling success'''
    if not self.device:
      return -1

    self.device.close()
    # TODO: Refactor this and the relevant part of __init__ into a setup() function
    self.device = None
    self.circ_buffer = [0] * SIZE_OF_CIRC_BUFFER
    self.cbuf_head = 0
    self.cbuf_tail = 0
    self.circ_buffer[0] = ord('\n')
    self.inside_escape = False
    return 0
