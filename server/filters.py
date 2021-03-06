from __future__ import division, print_function
from collections import deque
import numpy as np
from numpy.random import randn
from numpy.fft import rfft
from scipy import signal

#import matplotlib.pyplot as plt

class ButterFilter:

    def __init__(self):

        self.sig : deque = deque(np.zeros(10), maxlen=10)
        
        self.b, self.a = signal.butter(4, 0.5, analog=False)

    def push_data(self, data):

        self.sig.append(data)
        
        sig_ff = signal.filtfilt(self.b, self.a, self.sig, padlen=5)

        return sig_ff[9] 

if (False):
    b, a = signal.butter(2, 0.3, analog=False)

    # Show that frequency response is the same
    impulse = np.zeros(1000)
    impulse[500] = 1

    # Applies filter forward and backward in time
    imp_ff = signal.filtfilt(b, a, impulse)

    # Applies filter forward in time twice (for same frequency response)
    imp_lf = signal.lfilter(b, a, signal.lfilter(b, a, impulse))

    plt.subplot(2, 2, 1)
    plt.semilogx(20*np.log10(np.abs(rfft(imp_lf))))
    plt.ylim(-100, 20)
    plt.grid(True, which='both')
    plt.title('lfilter')

    plt.subplot(2, 2, 2)
    plt.semilogx(20*np.log10(np.abs(rfft(imp_ff))))
    plt.ylim(-100, 20)
    plt.grid(True, which='both')
    plt.title('filtfilt')

    sig = np.cumsum(randn(20))  # Brownian noise
    sig_ff = signal.filtfilt(b, a, sig, padlen=5)
    sig_lf = signal.lfilter(b, a, signal.lfilter(b, a, sig))
    plt.subplot(2, 1, 2)
    plt.plot(sig, color='silver', label='Original')
    plt.plot(sig_ff, color='#3465a4', label='filtfilt')
    plt.plot(sig_lf, color='#cc0000', label='lfilter')
    plt.grid(True, which='both')
    plt.legend(loc="best")
    plt.savefig('graph.png')
