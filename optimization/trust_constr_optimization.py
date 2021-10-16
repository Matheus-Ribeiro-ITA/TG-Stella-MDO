import os
import time
import numpy as np
from scipy.optimize import Bounds, minimize

import MDO
from optimization.functions import objectiveFun, callbackfun, callbackGenetic

# ----Process Time--------------------------------------------
startTime = time.time()

MDO.parseConfig("outputsConfig.cfg")
os.environ['fun_eval_count'] = '0'

print('{0:4s} | {1:8s} {2:8s} {3:8s} {4:9s} |'.format('Iter', 'Range', 'Var1', 'Var2', 'Var3'))

Xstates0 = np.array([6, 0.5, 0.68, 0.35,
                     1.5, 0.5, 0.5, 2,
                     0.8, 0.375, 0.375])

lb = [4, 0.4, 0.3, 0.3,
      0.5, 0.2, 0.2, 1,
      0.5, 0.2, 0.2]

ub = [6, 0.6, 0.75, 0.75,
      2.5, 0.7, 0.7, 2.5,
      1.5, 0.7, 0.7]

bounds = Bounds(lb, ub)

# res = differential_evolution(objectiveFun,
#                              bounds=bounds,
#                              callback=callbackGenetic,
#                              updating='immediate',  # Default = 'immediate'
#                              tol=1e-2,    # Default = 0.01
#                              popsize=15,  # Default = 15
#                              disp=True)

res = minimize(objectiveFun,
               Xstates0,
               method='trust-constr',
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
