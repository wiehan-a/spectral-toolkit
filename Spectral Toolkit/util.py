'''
Created on Aug 15, 2013

@author: Wiehan
'''
from numpy import *

primelist = [2, 3, 5, 7]

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
            
    