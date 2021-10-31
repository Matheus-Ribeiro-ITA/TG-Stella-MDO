import os
from configparser import ConfigParser
import numpy as np
import pandas as pd

import MDO
from main import main

history_df = pd.DataFrame()

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))

Nfeval = 1
Xstates_history = np.array([0.0]*4)  # TODO: Automate size of vector
outputs_history = np.array([0.0])

# ----logging--------------------------------------------
logger = MDO.createLog(name="genetic")
logger.info("------------------BEGIN------------------")


def objectiveFun(stateVars):

    stateVarsDict = {  # TODO: Create various cases
        'aspectRatio': stateVars[0]*10,
        'wingSecPercentage': 0.5,
        'wingArea': stateVars[1]*5,
        'taperRatio1': 1,
        'taperRatio2': 1,
        'aspectRatioV': 3.29,  # AR from top view
        'areaV': stateVars[2],  # Area from top view
        'taperV': 1,
        'posXV': stateVars[3]*5,
        'fuselageLength': 1.83
    }

    try:
        results_df = main(stateVarsDict, logger=logger)
        os.environ['fun_eval_count'] = str(int(os.getenv('fun_eval_count')) + 1)
        print(f"Call main {os.environ['fun_eval_count']}")
        # print(stateVars)
        print('Range km:', round(results_df.loc[0, 'range_all'], 1))
        print("")
        return -results_df['range_all'].iloc[0]/1000
    except:
        print('Deu ruim')
        return -1/1000



def callbackfun(Xstates, *_):
    global Nfeval, history_df, fb_history, outputs_history, time_history
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

    history_df = history_df.append(pd.Series(np.hstack((Xstates, objective_output))), ignore_index=True)
    history_df.to_csv("optimization/history/history.csv")
    # Xstates_history = np.vstack([Xstates_history, Xstates])
    # outputs_history = np.vstack([outputs_history, np.hstack([objective_output])])


# def callbackGenetic(Xstates, convergence=0.):
#     global Nfeval, Xstates_history, fb_history, outputs_history, time_history
#     objective_output = objectiveFun(Xstates)
#     dataStr = '{0:4d} | {1: 3.3f} {2:3.3f} {3:3.3f} {4:3.3f} |'.format(Nfeval,
#                                                                        objective_output,
#                                                                        Xstates[0],
#                                                                        Xstates[1],
#                                                                        Xstates[2])
#     print(dataStr)
#     logger.info(dataStr)
#
#     # Mostra o progresso da otimização
#     Nfeval += 1
#     # Acumula dados da otimização
#     Xstates_history = np.vstack([Xstates_history, Xstates])
#     outputs_history = np.vstack([outputs_history, np.hstack([objective_output])])
#
