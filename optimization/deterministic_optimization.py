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

# ------------------------------------------------------------------------------------------------
# Case 01: 4 var SLSQP
# scaleFactors = np.array([10, 5, 1, 5])
# ubFactor = 1.4
# lbFactor = 0.6
#
# # Xstates0 = np.multiply(np.array([7.07, 2.15, 0.41535, 2.05]), 1 / scaleFactors)
# Xstates0 = np.multiply(np.array([6, 2.5, 0.335, 1.85]), 1 / scaleFactors)
# os.environ['optimization_num_vars'] = '4'
# os.environ['optimization_type'] = 'SLSQP'
# ub = Xstates0*ubFactor
#
# lb = Xstates0*lbFactor
# ------------------------------------------------------------------------------------------------
# Case 02: 10 var SLSQP
os.environ['optimization_num_vars'] = '10'
os.environ['optimization_type'] = 'trust-constr_alcance'  # Change the otimization output name here
scaleFactors = np.array([10, 1, 5, 1, 1,
                         5, 1, 1, 5, 5])

# Xstates0 = np.multiply(np.array([7.07, 2.15, 0.41535, 2.05]), 1 / scaleFactors)
Xstates0 = np.multiply(np.array([6, 0.5, 2.5, 0.6, 0.6,
                                 3, 0.4, 0.6, 2, 2]), 1 / scaleFactors)

ub = np.multiply(np.array([14, 1, 3, 1, 1,
                           5, 1.5, 1, 2.5, 2]), 1 / scaleFactors)

lb = np.multiply(np.array([4, 0.3, 1, 0.3, 0.3,
                           1.5, 0.3, 0.3, 1, 0.8]), 1 / scaleFactors)
# ------------------------------------------------------------------------------------------------

bounds = Bounds(lb, ub)

res = minimize(objectiveFun,
               Xstates0,
               method='trust-constr',  # Change the otimization method here
               bounds=bounds,
               callback=callbackfun,
               tol=1e-6,
               options={'maxiter': 500,
                        'disp': True,
                        'eps': 10**-2})

desvars = res.x
print('---------------------')
print(res)
print('---------------------')
print(desvars)

# ---- Time-----------------------------------------
print(f"Process Time: {round((time.time() - startTime), 1)} s")
