function plot_RMS()
load('RMS1.mat')
load('RMS2.mat')
figure; hold on;
xlabel('RMS1'); ylabel('RMS2');
scatter(RMS1, RMS2);

end