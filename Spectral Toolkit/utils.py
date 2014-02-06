'''
Created on Aug 15, 2013

@author: Wiehan
'''
import numpy as np
import os, ctypes, sys, multiprocessing, matplotlib

if not globals().has_key("CPU_COUNT"):
    CPU_COUNT = multiprocessing.cpu_count()
    if sys.platform == "darwin":
        print "Multi-processing is buggy on Macs. Reverting to single-threaded computation."
        CPU_COUNT = 1
        
    print "Using", CPU_COUNT, "cpu cores"

primelist = [2, 3, 5, 7]

def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
def frequency_fmt(num):
    f = {
            -3 : 'nHhz',
            -2 : 'uHz',
            -1 : 'mHz',
            0 : 'Hz',
            1 : 'kHz',
            2 : 'MHz'
         }
    exponent = int(np.log10(num)/3)
    if num < 1:
        exponent -= 1
    num = num * 10**(-3*exponent)
    if exponent in f:
        return "%3.1f %s" % (num, f[exponent])
    else:
        return str(num)+" Hz"

def next_primes(n):
    global primelist
    if primelist[-1] >= n:
        return
    s = primelist[-1] + 2
    while s <= n:
        prime = True
        for p in primelist:
            if s % p == 0:
                prime = False
                break
        if prime:
            primelist.append(s)
        else:
            s += 2
 
def prime_factors(num):
    next_primes(ceil(sqrt(num)))
    factors = []
    global primelist
    i = 0
    while i < len(primelist):
        if num % primelist[i] == 0:
            factors.append(primelist[i])
            num /= primelist[i]
        elif num < primelist[i]:
            break
        else:
            i += 1
    print factors
    
def get_cpu_count():
    return CPU_COUNT
            
    