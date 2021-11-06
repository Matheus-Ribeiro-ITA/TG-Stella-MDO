import os
import time
import numpy as np
from scipy.optimize import differential_evolution, Bounds

import MDO
from optimization.functions import objectiveFun, callbackfun

# ----Process Time--------------------------------------------
startTime = time.time()

MDO.parseConfig("outputsConfig.cfg")
os.environ['fun_eval_count'] = '0'

print('{0:4s} | {1:8s} {2:8s} {3:8s} {4:9s} |'.format('Iter', 'Range', 'Var1', 'Var2', 'Var3'))

# ------------------------------------------------------------------------------------------------
# Case 01: 10 var SLSQP
os.environ['optimization_num_vars'] = '10'
os.environ['optimization_type'] = 'diff_evo'
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

# lb = [4, 0.4, 0.3, 0.3,
#       0.5, 0.2, 0.2, 1,
#       0.5, 0.2, 0.2]
#
# ub = [6, 0.6, 0.75, 0.75,
#       2.5, 0.7, 0.7, 2.5,
#       1.5, 0.7, 0.7]

bounds = Bounds(lb, ub)

options= {
    'grad': None,
    'xtol': 1e-08,
    'gtol': 1e-08,
    'barrier_tol': 1e-08,
    'sparse_jacobian': None,
    'maxiter': 1000,
    'verbose': 0,
    'finite_diff_rel_step': None,
    'initial_constr_penalty': 1.0,
    'initial_tr_radius': 1.0,
    'initial_barrier_parameter': 0.1, 'initial_barrier_tolerance': 0.1, 'factorization_method': None, 'disp': False}

res = differential_evolution(objectiveFun,
                             bounds=bounds,
                             callback=callbackfun,
                             updating='immediate',  # Default = 'immediate'
                             tol=1e-2,    # Default = 0.01
                             popsize=5)

desvars = res.x
print('---------------------')
print(res)
print('---------------------')
print(desvars)

# ---- Time-----------------------------------------
print(f"Process Time: {round((time.time() - startTime), 1)} s")
