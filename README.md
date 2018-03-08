# Myoeletric_Tetris
Tetris game with EMG control via SpikerBox

## Install hidapi
Myoelectric Tetris requires the Python `hidapi` library. The easiest way to get this library if you have Python already installed is through `pip`. 

```
pip install hidapi
```

## SpikerBox HID Manager
The `emg_buffer.py` script uses the `hid` library to read and buffer data from [MuscleSpikerBox](https://backyardbrains.com/products/muscleSpikerbox). `emg_buffer.py` is an almost-complete Python translation of Backyard Brain's [`HID_Manager` class](https://github.com/BackyardBrains/Spike-Recorder/blob/master/src/engine/HIDUsbManager.cpp).
