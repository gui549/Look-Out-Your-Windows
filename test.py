import os
#must set these before loading numpy:
# os.environ["OMP_NUM_THREADS"] = '8' # export OMP_NUM_THREADS=4
# os.environ["OPENBLAS_NUM_THREADS"] = '8' # export OPENBLAS_NUM_THREADS=4
# os.environ["MKL_NUM_THREADS"] = '8' # export MKL_NUM_THREADS=6
#os.environ["VECLIB_MAXIMUM_THREADS"] = '4' # export VECLIB_MAXIMUM_THREADS=4
#os.environ["NUMEXPR_NUM_THREADS"] = '4' # export NUMEXPR_NUM_THREADS=6

import numpy as np
import time

#np.__config__.show() #looks like I have MKL and blas
np.show_config()

start_time=time.time()
#test script:
a = np.random.randn(5000, 50000)
b = np.random.randn(50000, 5000)
ran_time=time.time()-start_time
print("time to complete random matrix generation was %s seconds" % ran_time)
np.dot(a, b) #this line should be multi-threaded
print("time to complete dot was %s seconds" % (time.time() - start_time - ran_time))