import os
from configparser import ConfigParser
import numpy as np
import pandas as pd

import MDO
from main import main

global historyDfFun

history_df = pd.DataFrame()
historyDfFun = pd.DataFrame()

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))

Nfeval = 1
Xstates_history = np.array([0.0]*4)  # TODO: Automate size of vector
outputs_history = np.array([0.0])

# ----logging--------------------------------------------
logger = MDO.createLog(name="genetic")
logger.info("------------------BEGIN------------------")


def objectiveFun(stateVars):
    global historyDfFun

    if os.environ['optimization_num_vars'] == '4':
        stateVarsDict = {
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
    elif os.environ['optimization_num_vars'] == '10':
        stateVarsDict = {
            'aspectRatio': stateVars[0]*10,
            'wingSecPercentage': stateVars[1]*1,
            'wingArea': stateVars[2]*5,
            'taperRatio1': stateVars[3]*1,
            'taperRatio2': stateVars[4]*1,
            'aspectRatioV': stateVars[5]*5,  # AR from top view
            'areaV': stateVars[6]*1,  # Area from top view
            'taperV': stateVars[7]*1,
            'posXV': stateVars[8]*5,
            'fuselageLength': stateVars[9]*5
        }

    try:
        results_df = main(stateVarsDict, logger=logger)
        os.environ['fun_eval_count'] = str(int(os.getenv('fun_eval_count')) + 1)
        # print(f"Call main {os.environ['fun_eval_count']}")
        # # print(stateVars)
        # print('Range km:', round(results_df.loc[0, 'range_all'], 1))
        # print("")

        if 'alcance' in os.environ['optimization_type']:
            historyDfFun = historyDfFun.append(
                pd.Series(np.hstack((stateVars, -results_df['range_all'].iloc[0] / 1000))), ignore_index=True)
            historyDfFun.to_csv(f"optimization/history/historyFun_{os.environ['optimization_num_vars']}_{os.environ['optimization_type']}.csv")
            return -results_df['range_all'].iloc[0]/1000
        elif 'pista' in os.environ['optimization_type']:
            historyDfFun = historyDfFun.append(
                pd.Series(np.hstack((stateVars, results_df['runway'].iloc[0] / 1000))), ignore_index=True)
            historyDfFun.to_csv(f"optimization/history/historyFun_{os.environ['optimization_num_vars']}_{os.environ['optimization_type']}.csv")
            return results_df['runway'].iloc[0] / 1000
        else:
            raise Exception("Fix optimization_type name")
    except:
        print('Deu ruim')
        if 'alcance' in os.environ['optimization_type']:
            return -1/1000
        else:
            return 2000/1000

def callbackfun(Xstates, *args, **kwargs):
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
    history_df.to_csv(f"optimization/history/history_{os.environ['optimization_num_vars']}_{os.environ['optimization_type']}.csv")
    # Xstates_history = np.vstack([Xstates_history, Xstates])
    # outputs_history = np.vstack([outputs_history, np.hstack([objective_output])])


def objectiveFunPymoo(stateVars):

    stateVarsDict = {
        'aspectRatio': stateVars[0]*10,
        'wingSecPercentage': stateVars[1]*1,
        'wingArea': stateVars[2]*5,
        'taperRatio1': stateVars[3]*1,
        'taperRatio2': stateVars[4]*1,
        'aspectRatioV': stateVars[5]*5,  # AR from top view
        'areaV': stateVars[6]*1,  # Area from top view
        'taperV': stateVars[7]*1,
        'posXV': stateVars[8]*5,
        'fuselageLength': stateVars[9]*5
    }

    try:
        results_df = main(stateVarsDict, logger=logger)
        return -results_df['range_all'].iloc[0]/1000, results_df['runway'].iloc[0] / 1000
    except:
        print('Deu ruim')
        return -1/1000, 1/1000
