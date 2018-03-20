function [left, right, turn] = emg_control(emg_1, emg_2)
left = 0;
right = 0;
turn = 0;

gain_1 = 1;
gain_2 = 1;

rms_1 = rms(gain_1 * emg_1);
rms_2 = rms(gain_2 * emg_2);

%RMS1(end+1) = rms_1;
%RMS2(end+1) = rms_2;

if rms_1/rms_2 > 1.8
    right = 1;
elseif rms_1/rms_2 < 0.8
    left = 1;
elseif rms_1/rms_2 > 0.8 && rms_1/rms_2 < 1.8
    turn = 1;
end
end