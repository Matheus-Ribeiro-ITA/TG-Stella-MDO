import time
import numpy as np
from scipy.optimize import Bounds, minimize

import MDO
from optimization.functions import objectiveFun, callbackfun
# ----Process Time--------------------------------------------
startTime = time.time()

MDO.parseConfig("outputsConfig.cfg")

print('{0:4s} | {1:8s} {2:8s} {3:8s} {4:9s} |'.format('Iter', 'Range', 'Var1', 'Var2', 'Var3'))

Xstates0 = np.array([6.0/10, 0.68, 0.35])

bounds = Bounds([4/10, 0.4, 0.2],
                [8/10, 0.8, 0.5])

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
print(f"Process Time: {round((time.time() - startTime),1)} s")
