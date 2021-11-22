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

    df_results = pd.DataFrame()

    failed_count = 0

    for ii in range(n_samples):
        print(f"Case {ii-failed_count}/{ii}/{n_samples}, Time used: {round(time.time() -startTime, 2)} s")
        # Evaluate sample
        try:
            results_to_append = main(list(X[ii, :]), logger=logger)
        except:
            print(f"SKIPPING Case {ii}/{n_samples}, Time used: {round(time.time() -startTime, 2)} s")
            failed_count += 1
            continue
        states_to_append = pd.DataFrame(dict(zip(inputs_names, X[ii, :])), index=[0])
        results_to_append = pd.concat([states_to_append, results_to_append], axis=1)

        # df_results[len(df_results.index)] = results_list
        df_results = df_results.append(results_to_append, ignore_index=True)

        df_results.to_csv(f'DOE/database/{filename}.csv', index=False)

    print(f"Done {n_samples - failed_count}/{n_samples}")


if __name__ == '__main__':
    # ----Process Time--------------------------------------------
    startTime = time.time()

    # ----logging--------------------------------------------
    logger = MDO.createLog(name="doe")
    logger.info("------------------BEGIN------------------")

    # ----Config ----------------------------------------------
    MDO.parseConfig("outputsConfig.cfg")

    n_samples = 1500

    # ---------------------------------------------------------------
    # Case all variables
    inputs_names = ['aspectRatio', 'wingSecPercentage', 'wingArea', 'taperRatio1', 'taperRatio2',
                    'aspectRatioV', 'areaV', 'taperV', 'posXV',
                    'fuselageLength']

    n_inputs = len(inputs_names)

    lb = [4, 0.3, 0.6, 0.3, 0.3,
          3, 0.2, 0.5, 0.5,
          1]
    ub = [14, 0.8, 3.0, 1.0, 1.0,
          6, 1.5, 1, 2.5,
          2]

    sampling_type = 'real_random'

    run_doe(n_inputs=n_inputs, lb=lb, ub=ub,
            n_samples=n_samples, sampling_type=sampling_type,
            logger=logger, inputs_names=inputs_names,
            filename='resultsAll')

    # ---------------------------------------------------------------
    # Case: Wing only
    inputs_names = ['aspectRatio', 'wingSecPercentage', 'wingArea', 'taperRatio1', 'taperRatio2',
                    'aspectRatioV', 'areaV', 'taperV', 'posXV',
                    'fuselageLength']

    n_inputs = len(inputs_names)

    lb = [4, 0.3, 0.8, 0.3, 0.3,
          4, 0.6, 0.6, 1.5,
          1.5]
    ub = [14, 0.8, 3.0, 1.0, 1.0,
          4, 0.6, 0.6, 1.5,
          1.5]

    sampling_type = 'real_random'

    run_doe(n_inputs=n_inputs, lb=lb, ub=ub,
            n_samples=n_samples, sampling_type=sampling_type,
            logger=logger, inputs_names=inputs_names,
            filename='resultsWing')

    # ---------------------------------------------------------------
    # Case: Stabilizer only
    inputs_names = ['aspectRatio', 'wingSecPercentage', 'wingArea', 'taperRatio1', 'taperRatio2',
                    'aspectRatioV', 'areaV', 'taperV', 'posXV',
                    'fuselageLength']

    n_inputs = len(inputs_names)

    lb = [7, 0.5, 2, 0.6, 0.6,
          3, 0.4, 0.5, 0.5,
          1.5]
    ub = [7, 0.5, 2, 0.6, 0.6,
          6, 1, 0.8, 2.5,
          1.5]

    sampling_type = 'real_random'

    run_doe(n_inputs=n_inputs, lb=lb, ub=ub,
            n_samples=n_samples, sampling_type=sampling_type,
            logger=logger, inputs_names=inputs_names,
            filename='resultsStab')

    # ---------------------------------------------------------------
    # Case: Fuselage only
    inputs_names = ['aspectRatio', 'wingSecPercentage', 'wingArea', 'taperRatio1', 'taperRatio2',
                    'aspectRatioV', 'areaV', 'taperV', 'posXV',
                    'fuselageLength']

    n_inputs = len(inputs_names)

    lb = [7, 0.5, 2, 0.6, 0.6,
          4, 0.6, 0.7, 1.5,
          1.0]
    ub = [7, 0.5, 2, 0.6, 0.6,
          4, 0.6, 0.7, 1.5,
          2.5]

    sampling_type = 'real_random'

    run_doe(n_inputs=n_inputs, lb=lb, ub=ub,
            n_samples=n_samples, sampling_type=sampling_type,
            logger=logger, inputs_names=inputs_names,
            filename='resultsFuselage')
