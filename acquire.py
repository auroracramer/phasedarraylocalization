#!/usr/bin/env python
from __future__ import division
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pyaudio
import Queue
#import threading
import multiprocessing
import time
import sys
from numpy import *
from scipy import *
import scipy.signal as signal
from rtlsdr import RtlSdr
from numpy.fft import *


def recordSamples(sdr, N_samples, y, chunk_size=1024):
    samples_acquired = 0
    # Acquire the samples from an SDR
    while samples_acquired < N_samples:
        y.put(sdr.read_samples(chunk_size))
        samples_acquired += chunk_size


def acquireSamplesAsync(fs, fc, t_total, chunk_size=1024, num_SDRs=3, gain=36):
    SDRs = []

    # Initialize the SDRs
    for i in xrange(num_SDRs):
        sdr_i = RtlSdr(device_index=i)
        sdr_i.sample_rate = fs
        sdr_i.center_freq = fc
        sdr_i.gain = gain
        SDRs.append(sdr_i)

    # Setup the output queues
    output_queues = [Queue.Queue() for _ in xrange(num_SDRs)]

    rec_thrds = []

    # Create the thread objects for acquisition
    for i, sdr_i in enumerate(SDRs):
        y = output_queues[i]
        sdr_rec = multiprocessing.process(target=recordSamples, \
                                   args=(sdr_i, N_samples, y, chunk_size))
        rec_thrds.append(sdr_rec)

    # Start the threads
    for rec_thread in rec_thrds:
        rec_thread.start()

    # Clean up the SDR objects
    for sdr in SDRs:
        sdr.close()


    return output_queues


if __name__ == "__main__":
    acquireSamplesAsync(fs=1e6, fc=96.3e6, t_total=4)
    exit(0)
