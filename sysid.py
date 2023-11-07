from scipy.optimize import basinhopping
import scipy.signal
import dill
import numpy as np
import matplotlib.pyplot as plt

def mse(yTrue, yPred):
    return np.mean((yTrue-yPred)**2)

def modelSim(x, Ts, t):
    na = nb = len(x)//2
    num = x[0:na]
    den = np.r_[1, x[na:]]

    Pd = scipy.signal.TransferFunction(num, den, dt=Ts)
    #print(Pd)

    t, y = scipy.signal.dstep(Pd, t=t)
    y = np.squeeze(y)

    return t, y

def modelCompare(x, t, yTrue, Ts):
    _, yPred = modelSim(x, Ts, t)

    return mse(yTrue, yPred)

def main():
    with open('results.dill', 'rb') as dillFile:    
        t, y, Ts = dill.load(dillFile)

    f = lambda x: modelCompare(x, t, y, Ts)
    x0 = [1, 1] # first order model, na=nb=1

    minimizer_kwargs = {"method": "BFGS"}
    res = basinhopping(f, x0, minimizer_kwargs=minimizer_kwargs, niter=200)

    print('=== OPTIMIZATION RESULTS ===')
    print(res)
    print('=== MODEL RESULTS ===')
    print(res.x)

    tm, ym = modelSim(res.x, Ts, t)

    # Plot time response
    plt.figure()
    plt.step(tm, ym)
    plt.step(t, y)
    plt.ylabel('Temperatura(t)')
    plt.xlabel('t(s)')
    plt.show()




if __name__ == "__main__":
    main()