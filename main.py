import time
from _collections import OrderedDict
import numpy as np
import pandas as pd

from aircraftInfo import AircraftInfo
import MDO


def main(x_states, logger=None):
    # ----Vertical Stabilizer-------------------------------------
    # Options: "conventional", "v".
    # Warning: option "h" is broken
    verticalType = "v"

    # --Airfoils------------------------------------------------
    wingAirfoil = "ls417mod_cruise"
    stabAirfoil = "naca0012_cruise"

    # ----Variables Optimizer---------------------------------------
    wingSpan = x_states[0]
    wingSecPercentage = x_states[1]
    wingRootChord = x_states[2]
    wingTipChord = x_states[3]
    wingMiddleChord = (wingRootChord + wingTipChord) / 2

    horizontalSpan = x_states[4]
    horizontalRootChord = x_states[5]
    horizontalTipChord = x_states[6]
    horizontalXPosition = x_states[7]

    verticalSpan = x_states[8]
    verticalRootChord = x_states[9]
    verticalTipChord = x_states[10]

    # endPlateTipChord = 0.4

    wingSecPosition = wingSpan / 2 * wingSecPercentage
    wingPosSec = wingSpan / 2 * (1 - wingSecPercentage)

    # ----Config---------------------------------------
    cgCalc = 0.25

    # ----Parser to dict---------------------------------------
    stateVariables, controlVariables, avlCases, engineInfo, missionProfile = MDO.set_state_variables(
        wingRootChord=wingRootChord, wingAirfoil=wingAirfoil, wingMiddleChord=wingMiddleChord,
        wingSecPosition=wingSecPosition, wingTipChord=wingTipChord, wingPosSec=wingPosSec,
        horizontalRootChord=horizontalRootChord, horizontalXPosition=horizontalXPosition,
        horizontalTipChord=horizontalTipChord,
        horizontalSpan=horizontalSpan, verticalRootChord=verticalRootChord, verticalTipChord=verticalTipChord,
        verticalSpan=verticalSpan, stabAirfoil=stabAirfoil
    )

    # ---- Aircraft Info Class ----------------------------------------

    aircraftInfo = AircraftInfo(stateVariables, controlVariables, engineInfo=engineInfo)
    aircraftInfo.cg.calc = cgCalc

    # ---- Avl -----------------------------------------
    results = MDO.avlMain(aircraftInfo, avlCases, verticalType=verticalType)

    # ---- Results -----------------------------------------
    output_dict = MDO.mainResults(results=results, aircraftInfo=aircraftInfo, avlCases=avlCases,
                                  missionProfile=missionProfile, logger=logger)

    return pd.DataFrame(output_dict, index=[0])


if __name__ == '__main__':
    # ----Process Time--------------------------------------------
    startTime = time.time()

    # ----logging--------------------------------------------
    logger = MDO.createLog(name="main")
    logger.info("------------------BEGIN------------------")

    # ----Config ----------------------------------------------
    MDO.parseConfig("outputsConfig.cfg")

    num_states = 10
    x_states = np.array([0.0] * num_states)

    x_states[0] = 6  # wingSpan = 6
    x_states[1] = 0.5  # wingSecPercentage = 0.5
    x_states[2] = 0.68  # wingRootChord = 0.68
    x_states[3] = 0.35  # wingTipChord = 0.35
    wingMiddleChord = (x_states[2] + x_states[3]) / 2

    x_states[4] = 1.5  # horizontalSpan = 1.5
    x_states[5] = 0.5  # horizontalRootChord = 0.5
    x_states[6] = 0.5  # horizontalTipChord = 0.5
    x_states[7] = 2  # horizontalXPosition = 2

    x_states[8] = 0.8  # verticalSpan = 0.8 Remember that is H vertical
    x_states[9] = 0.375  # verticalRootChord = 0.375
    x_states[10] = 0.375  # verticalTipChord = 0.375

    # endPlateTipChord = 0.4  # endPlateTipChord = 0.4

    wingSecPosition = x_states[0] / 2 * x_states[1]
    wingPosSec = x_states[0] / 2 * (1 - x_states[1])

    main(x_states)

    # ---- Time-----------------------------------------
    print(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info("------------------END------------------")
