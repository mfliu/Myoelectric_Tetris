# Myoeletric_Tetris
Tetris game with EMG control via SpikerBox

## Install hidapi
Myoelectric Tetris requires the Python `hidapi` library. The easiest way to get this library if you have Python already installed is through `pip`. 

```
pip install hidapi
```

## SpikerBox HID Manager
The `emg_buffer.py` script uses the `hid` library to read and buffer data from [MuscleSpikerBox](https://backyardbrains.com/products/muscleSpikerbox). `emg_buffer.py` is an almost-complete Python translation of Backyard Brain's [`HID_Manager` class](https://github.com/BackyardBrains/Spike-Recorder/blob/master/src/engine/HIDUsbManager.cpp).

## Running Tetris
Tetris for this game is implemented in MATLAB, primarily via [`matlabtetris`](https://www.mathworks.com/matlabcentral/fileexchange/34513-matlabtetris). However, the keyboard controls are replaced with an EMG signal classifier in `emg_control.m`. The time window of EMG signal to use for classification is set via `set_window_size.m`. EMG data is buffered for the window size set in milliseconds. This raw EMG signal is then passed to `emg_control.m` where signal is classified as moving a Tetris piece to the left or right, or turning the Tetris piece clockwise. For most implementations of this game, EMG electrodres are placed on a flexor-extensor pair on the forearm. Wrist flexion corresponds to moving the Tetris piece to the left, wrist extension moves the Tetris piece to the right, and co-contraction of the flexor and extensor rotates the piece in a clockwise direction. All other keyboard controls for the game (moving down, pausing) remain the same.