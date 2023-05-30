clc;
clear;
close all;

att = table2array(readtable('attackerpayoff.csv'));
def = table2array(readtable('defenderpayoff.csv'));

res = 1:10;

a_avg = transpose(transpose(att) ./ res);
d_avg = def ./ res;

mesh(att);
title('Average Attacker Payoffs');
xlabel('Attacker Resources');
ylabel('Defender Resources');
zlabel('Payoff');

figure();
mesh(def);
title('Average Defender Payoffs');
xlabel('Attacker Resources');
ylabel('Defender Resources');
zlabel('Payoff');

figure();
mesh(a_avg);
title('Average Payoff Per Resource - Attacker');
xlabel('Attacker Resources');
ylabel('Defender Resources');
zlabel('Payoff/Resource');

figure();
mesh(d_avg);
title('Average Payoff Per Resource - Defender');
xlabel('Attacker Resources');
ylabel('Defender Resources');
zlabel('Payoff/Resource');
