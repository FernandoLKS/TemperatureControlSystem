# -*- coding: utf-8 -*-
"""
Exemplo de controle PI (proporcional integral)

Processo de primeira ordem - temperatura ("secador de cabelo")
Y(s)/U(s) = 1/(10*s + 1)

@author: Prof. Daniel Cavalcanti Jeronymo
"""

import time
import scipy.signal
import numpy as np
import math
import matplotlib.pyplot as plt
import aarc

# Defina o intervalo de valores desejado
valor_inicial = 54
valor_final = 30
quantidade_de_valores = 35  # Você pode ajustar esse valor conforme necessário

# Crie a sequência de valores usando linspace
valores_y = np.linspace(0, 1, quantidade_de_valores)

# Inverta a sequência para que o valor 54 corresponda a 0 e o valor 20 corresponda a 1
valores_y = 1 - valores_y

# Continuous transfer function of a process
P = scipy.signal.TransferFunction([0.00371099], [0.99621047, 1])

port, _ = aarc.dac_initialize()

# Discrete process for simulation
Ts = 0.1                    # time step
Pd = P.to_discrete(Ts)

B = Pd.num                  # zeros
A = Pd.den                  # poles
nb = len(B) - 1             # number of zeros
na = len(A) - 1             # number of poles

# Simulation parameters
tf = 20

Reference = 35
r = (Reference - 54) * (-1 / 20)

k = 0.00371099
tau = 0.99621047
ts = Ts
theta = ts
t = tau

# 1942, Ziegler, Nichols, Optimum Settings for Automatic Controllers
#kp = 0.9*tau/ts
#ti = 3.3*ts # or ts/0.3

# 1986, Rivera, Morari, Skogestad, Internal Model Control: Pid Controller Design - precursor to SIMC
#kp = (2*t + theta)/(2*theta*k)
#ti = min(t+theta/2, 8*theta) # min with 8*theta comes from a later suggestion from SIMC

# 2001, Skogestad, Probably the best simple PID tuning rules in the world - SIMC PI - Skogestad IMC or Simple IMC
tauc = 40*theta # 20*theta for 20x slower response
kp = (1/k)*(tau/(tauc+theta))
ti = min(tau, 4*(tauc+theta))

# 2011, Skogestald, Grimholt, The SIMC Method for Smooth PID Controller Tuning, Table 1
#kp = (1/k)*(1/(4*(tauc+theta)**2))
#ti = 4*(tauc+theta)
#td = 4*(tauc+theta)

# 1953, Cohen, Coon, Theoretical Consideration of Retarded Control
#kp = (t/theta)*(0.9 + theta/(12*t))/k
#ti = theta*(30+3/t)/(13+8/t)

ki = kp/ti # IDEAL FORM

lastErro = 0 
lastOutput = 0

while True:
    y = aarc.dac_receive_data(port, 0, True)

    pos = int(y) - valor_final

    y = (y - 54) * (-1 / 20)
    
    # error
    error = r - y
    
    # PI control discretized by backwards differences
    #du = kp*(e[k] - e[k-1])  + ki*e[k]*Ts
    du = (kp + ki*Ts)*error - kp*lastErro

    output = lastOutput + du

    if(output < 0):
        output = 0
    elif(output> 5):
        output = 5

    aarc.dac_send_data(port, 0, output)

    lastErro = error
    lastOutput = output

    print(output,error )
