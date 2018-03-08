clear all; close all; clc;
clear classes;
mod = py.importlib.import_module('emg_buffer');
py.importlib.reload(mod);

if count(py.sys.path,'') == 0
    insert(py.sys.path,int32(0),'');
end

sb = py.emg_buffer.SpikerBox();

o_v = sb.open_device();

emg_1 = [];
emg_2 = [];
figure; hold on;
plot(emg_1);
plot(emg_2);

for i = 1:10000
 emg_batch = sb.read_buffer();
 emg_batch_data = cell(emg_batch(2));
 emg_batch_channels = cell(emg_batch_data{1, 1});
 emg_matlab_doubles = [];
 for j = 1:length(emg_batch_channels)
     cell_value = emg_batch_channels(j);
     value = double(cell_value{1, 1});
     emg_matlab_doubles(end+1) = value;
 end
 channel1 = emg_matlab_doubles(1:2:end);
 channel2 = emg_matlab_doubles(2:2:end);
 emg_1 = [emg_1 channel1];
 emg_2 = [emg_2 channel2];
 
 plot(i:i+length(channel1)-1, channel1);
 plot(i:i+length(channel2)-1, channel2);
 linkdata on;
 pause(0.0005);
end
c_v = sb.close_device();
