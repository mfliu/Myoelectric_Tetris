import emg_buffer

sb = emg_buffer.SpikerBox()
sb.open_device()
data = []
for i in range(0, 10000):
	r = sb.read_buffer()
	data.extend(r)
print(data)
sb.close_device()