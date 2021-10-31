import os
import time
import numpy as np
from scipy.optimize import Bounds, minimize

import MDO
from optimization.functions import objectiveFun, callbackfun

# ----Process Time--------------------------------------------
startTime = time.time()

MDO.parseConfig("outputsConfig.cfg")
os.environ['fun_eval_count'] = '0'

print('{0:4s} | {1:8s} {2:8s} {3:8s} {4:9s} |'.format('Iter', 'Range', 'Var1', 'Var2', 'Var3'))

Xstates0 = np.array([7.07/10, 2.15/5, 0.41535, 2.05/5])

ub = np.array([7.07*1.4/10,
               2.15*1.4/5,
               0.41535*1.4,
               2.05*1.4/5])

lb = np.array([7.07*0.6/10,
               2.15*0.6/5,
               0.41535*0.6,
               2.05*0.6/5])

bounds = Bounds(lb, ub)

res = minimize(objectiveFun,
               Xstates0,
               method='SLSQP',
               bounds=bounds,
               callback=callbackfun,
               tol=1e-2,
               options={'maxiter': 200, 'disp': True})

desvars = res.x
print('---------------------')
print(res)
print('---------------------')
print(desvars)

# ---- Time-----------------------------------------
print(f"Process Time: {round((time.time() - startTime), 1)} s")
