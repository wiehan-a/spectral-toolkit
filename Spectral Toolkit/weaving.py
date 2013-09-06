'''
Created on Sep 5, 2013

@author: Wiehan
'''

if __name__ == '__main__':
#     import scipy.weave as weave
#     a = 1
#     weave.inline('printf("%d\\n",a);',['a'])
    from math import sqrt
    from joblib import Parallel, delayed
    Parallel(n_jobs=8)(delayed(sqrt)(i**2) for i in range(10000000))