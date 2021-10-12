"""
Script to run DOE for the project
"""

import numpy as np
import pandas as pd
from pymoo.factory import get_sampling
from pymoo.interface import sample
import time

from main import main
import MDO

#=========================================

# SETUP

# Define design function
# def des_funcs(Xinp):
#
#     x1, x2, x3 = Xinp
#
#     f1 = x1**2 + (x2-2)**2 - 0.0001*x3
#
#     f2 = -x2**2
#
#     # Returns
#     return f1, f2


def run_doe(n_inputs=None, lb=None, ub=None, n_samples=None, sampling_type=None,
            logger=None, filename='results', inputs_names=None):

    # Set random seed to make results repeatable
    np.random.seed(123)

    # Initialize sampler
    sampling = get_sampling(sampling_type)

    # Draw samples
    X = sample(sampling, n_samples, n_inputs)

    # Samples are originally between 0 and 1,
    # so we need to scale them to the desired interval
    for ii in range(n_inputs):
        X[:,ii] = lb[ii] + (ub[ii] - lb[ii])*X[:,ii]

    # Execute all cases and store outputs
    f1_samples = []
    f2_samples = []

    df_results = pd.DataFrame()

    for ii in range(n_samples):
        print(f"Case {ii}/{n_samples}, Time used: {round(time.time() -startTime, 2)} s")
        # Evaluate sample
        try:
            results_to_append = main(X[ii,:], logger=logger)
        except ValueError:
            print(f"SKIPPING Case {ii}/{n_samples}, Time used: {round(time.time() -startTime, 2)} s")
            continue
        states_to_append = pd.DataFrame(dict(zip(inputs_names, X[ii,:])), index=[0])
        results_to_append = pd.concat([states_to_append, results_to_append], axis=1)

        # df_results[len(df_results.index)] = results_list
        df_results = df_results.append(results_to_append, ignore_index=True)

        df_results.to_csv(f'DOE/database/{filename}.csv', index=False)

    # # Create a pandas dataframe with all the information
    # df = pd.DataFrame({'x1' : X[:,0],
    #                    'x2' : X[:,1],
    #                    'x3' : X[:,2],
    #                    'f1' : f1_samples,
    #                    'f2' : f2_samples})


if __name__ == '__main__':
    # ----Process Time--------------------------------------------
    startTime = time.time()

    # ----logging--------------------------------------------
    logger = MDO.createLog(name="doe")
    logger.info("------------------BEGIN------------------")

    # ----Config ----------------------------------------------
    MDO.parseConfig("outputsConfig.cfg")

    n_inputs = 11

    inputs_names = ['wingSpan', 'wingSecPercentage', 'wingRootChord', 'wingTipChord',
                    'horizontalSpan', 'horizontalRootChord', 'horizontalTipChord', 'horizontalXPosition',
                    'verticalSpan', 'verticalRootChord', 'verticalTipChord']

    lb = [4, 0.4, 0.3, 0.3,
          0.5, 0.2, 0.2, 0.5,
          0.5, 0.2, 0.2]

    ub = [6, 0.6, 0.75, 0.75,
          2.5, 0.7, 0.7, 2.5,
          1.5, 0.7, 0.7]

    n_samples = 1000

    sampling_type = 'real_random'

    run_doe(n_inputs=n_inputs, lb=lb, ub=ub, n_samples=n_samples, sampling_type=sampling_type,
            logger=logger, inputs_names=inputs_names)