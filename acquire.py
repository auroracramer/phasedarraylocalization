#!/usr/bin/env python
from __future__ import division
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pyaudio
#import Queue

#from multiprocessing import Process, Queue
import threading
from Queue import Queue
import time
import sys
from numpy import *
from scipy import *
import scipy.signal as signal
from rtlsdr import RtlSdr
from numpy.fft import *
import cPickle



def recordSamples(sdr, idx, N_samples, y, chunk_size=1024):
    samples_acquired = 0
    # Acquire the samples from an SDR
    while samples_acquired < N_samples:
        print "SDR %d: Acquired %d samples." % (idx, samples_acquired)
        y.put(sdr.read_samples(chunk_size))
        samples_acquired += chunk_size

    sdr.close()
    #y.close()
    #y.join_thread()
    print "SDR %d: Closed as fuck." % idx
    sys.stdout.flush()

    return


def acquireSamplesAsync(fs, fc, t_total, chunk_size=1024, num_SDRs=3, gain=36):
    assert type(t_total) == int, "Time must be an integer."
    N_samples = 1024000*t_total
    SDRs = []

    # Initialize the SDRs
    for i in xrange(num_SDRs):
        sdr_i = RtlSdr(device_index=i)
        sdr_i.sample_rate = fs
        sdr_i.center_freq = fc
        sdr_i.gain = gain
        SDRs.append(sdr_i)

    # Setup the output queues
    output_queues = [Queue() for _ in xrange(num_SDRs)]

    rec_thrds = []

    # Create the thread objects for acquisition
    for i, sdr_i in enumerate(SDRs):
        y = output_queues[i]
        sdr_rec = threading.Thread(target=recordSamples, \
                          args=(sdr_i, i, N_samples, y, chunk_size))
        rec_thrds.append(sdr_rec)

    # Start the threads
    for rec_thread in rec_thrds:
        rec_thread.start()


    """
    last_size = [0 for _ in xrange(num_SDRs)]
    done_arr = [False for _ in xrange(num_SDRs)]
    """
    # Wait until threads are done
    while any([thrd.is_alive() for thrd in rec_thrds]):
        time.sleep(1)
        """
        for i, size in enumerate(last_size):
            curr_size = output_queues[i].qsize()
            if not done_arr[i] and size == curr_size:
                #rec_thrds[i].terminate()
                done_arr[i] = True
            else:
                last_size[i] = curr_size
        """




    # Clean up the SDR objects
    """
    for sdr in SDRs:
        sdr.close()
    """
    # For DEBUG
    samples = []
    for i, q in enumerate(output_queues):
        print "Printing Queue %d" % i
        print "\t- Queue size: %d" % q.qsize()
        samples.append([])
        while not q.empty():
            print q.qsize()
            samples[i] += list(q.get())

        print "Done"


    with open("parallel_samps.pkl", "wb") as f:
        cPickle.dump(samples, f)

    return output_queues


if __name__ == "__main__":
    acquireSamplesAsync(fs=1e6, fc=443.61e6, t_total=3, gain=60, num_SDRs=2)
    exit(0)
