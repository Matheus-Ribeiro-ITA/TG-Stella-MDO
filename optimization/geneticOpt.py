import os
import time
import numpy as np
from scipy.optimize import differential_evolution, Bounds

import MDO
from optimization.functions import objectiveFun, callbackfun, callbackGenetic

# ----Process Time--------------------------------------------
startTime = time.time()

MDO.parseConfig("outputsConfig.cfg")
os.environ['fun_eval_count'] = '0'

print('{0:4s} | {1:8s} {2:8s} {3:8s} {4:9s} |'.format('Iter', 'Range', 'Var1', 'Var2', 'Var3'))

lb = [4, 0.4, 0.3, 0.3,
      0.5, 0.2, 0.2, 1,
      0.5, 0.2, 0.2]

ub = [6, 0.6, 0.75, 0.75,
      2.5, 0.7, 0.7, 2.5,
      1.5, 0.7, 0.7]

bounds = Bounds(lb, ub)

options= {
    'grad': None,
    'xtol': 1e-08,
    'gtol': 1e-08,
    'barrier_tol': 1e-08,
    'sparse_jacobian': None,
    'maxiter': 1000, 'verbose': 0, 'finite_diff_rel_step': None, 'initial_constr_penalty': 1.0, 'initial_tr_radius': 1.0, 'initial_barrier_parameter': 0.1, 'initial_barrier_tolerance': 0.1, 'factorization_method': None, 'disp': False}

res = differential_evolution(objectiveFun,
                             bounds=bounds,
                             callback=callbackGenetic,
                             updating='immediate',  # Default = 'immediate'
                             tol=1e-2,    # Default = 0.01
                             popsize=15,  # Default = 15
                             disp=True)

desvars = res.x
print('---------------------')
print(res)
print('---------------------')
print(desvars)

# ---- Time-----------------------------------------
print(f"Process Time: {round((time.time() - startTime), 1)} s")
