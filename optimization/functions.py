import os
from configparser import ConfigParser
import matplotlib.pyplot as plt
import math
from _collections import OrderedDict
import numpy as np

from aircraftInfo import AircraftInfo
import MDO
from main import main

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))

Nfeval = 1
Xstates_history = np.array([0.0]*11)
outputs_history = np.array([0.0])

# ----logging--------------------------------------------
logger = MDO.createLog(name="genetic")
logger.info("------------------BEGIN------------------")


def objectiveFun(stateVars):

    try:
        results_df = main(stateVars, logger=logger)
        os.environ['fun_eval_count'] = str(int(os.getenv('fun_eval_count')) + 1)
        print(f"Call main {os.environ['fun_eval_count']}")
        # print(stateVars)
        print(round(results_df['range_all'].iloc[0]/1000, 1))
        print("")
        return -results_df['range_all'].iloc[0]
    except:
        print('Deu ruim')
        return -1



def callbackfun(Xstates, *_):
    global Nfeval, Xstates_history, fb_history, outputs_history, time_history
    objective_output = objectiveFun(Xstates)
    dataStr = '{0:4d} | {1: 3.3f} {2:3.3f} {3:3.3f} {4:3.3f} |'.format(Nfeval,
                                                                       objective_output,
                                                                       Xstates[0],
                                                                       Xstates[1],
                                                                       Xstates[2])
    print(dataStr)
    logger.info(dataStr)

    # Mostra o progresso da otimização
    Nfeval += 1
    # Acumula dados da otimização
    Xstates_history = np.vstack([Xstates_history, Xstates])
    outputs_history = np.vstack([outputs_history, np.hstack([objective_output])])


def callbackGenetic(Xstates, convergence=0.):
    global Nfeval, Xstates_history, fb_history, outputs_history, time_history
    objective_output = objectiveFun(Xstates)
    dataStr = '{0:4d} | {1: 3.3f} {2:3.3f} {3:3.3f} {4:3.3f} |'.format(Nfeval,
                                                                       objective_output,
                                                                       Xstates[0],
                                                                       Xstates[1],
                                                                       Xstates[2])
    print(dataStr)
    logger.info(dataStr)

    # Mostra o progresso da otimização
    Nfeval += 1
    # Acumula dados da otimização
    Xstates_history = np.vstack([Xstates_history, Xstates])
    outputs_history = np.vstack([outputs_history, np.hstack([objective_output])])

