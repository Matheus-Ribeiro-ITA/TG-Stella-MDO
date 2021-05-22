import time
import numpy as np
from scipy.optimize import differential_evolution, Bounds

import MDO
from optimization.functions import objectiveFun, callbackfun, callbackGenetic

# ----Process Time--------------------------------------------
startTime = time.time()

MDO.parseConfig("outputsConfig.cfg")

print('{0:4s} | {1:8s} {2:8s} {3:8s} {4:9s} |'.format('Iter', 'Range', 'Var1', 'Var2', 'Var3'))

# Xstates0 = np.array([6.0 / 10, 0.68, 0.35])

bounds = Bounds([6 / 10, 0.5, 0.3],
                [8 / 10, 0.8, 0.5])

res = differential_evolution(objectiveFun,
                             bounds=bounds,
                             callback=callbackGenetic,
                             updating='deferred',
                             tol=1e-2,
                             disp=True)

desvars = res.x
print('---------------------')
print(res)
print('---------------------')
print(desvars)

# ---- Time-----------------------------------------
print(f"Process Time: {round((time.time() - startTime), 1)} s")
