import numpy as np
import matplotlib.pyplot as plt
import time
import aarc
import dill

port,_ = aarc.dac_initialize()

ts = 0.1                     # sample time
tf = 1000                   # final time - number of samples = tf/ts
y = np.arange(0, tf, ts)     # measurements
t = np.arange(0, tf, ts)

Nsteps = len(y)

# using time() instead of process_time() because Serial reading occurs outside of the script
t0 = time.time()

for i in range(Nsteps):
    time.sleep(ts)
    # acquire a new measure from sensor
    y[i] = aarc.dac_receive_data(port, 0, True)
    # send a signal to the actuator
    u = 5
    aarc.dac_send_data(port, 0, u)

tdiff = time.time() - t0

aarc.dac_send_data(port, 0, 0)

with open('results.dill', 'wb') as dillFile:
    dill.dump((t, y, ts), dillFile)

print('y: ')
print(y)
print('Calculated sample time Ts: ', tdiff/i)