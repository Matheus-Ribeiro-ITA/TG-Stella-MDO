import os
import time
from _collections import OrderedDict
import numpy as np
import pandas as pd
from configparser import ConfigParser

from aircraftInfo import AircraftInfo
import MDO

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))


def main(x_states_global, logger=None, x_states_default_values=None):
    # ----Vertical Stabilizer-------------------------------------
    # Options: "conventional", "v".
    # Warning: option "H" is broken
    verticalType = "v"

    # --Airfoils------------------------------------------------
    # wingAirfoil = "ls417mod_cruise"  # Stella Airfoil
    wingAirfoil = "naca4415_cruise"  # Shadow 200 Airfoil  # TODO: Create airfoil variable to main()

    stabAirfoil = "naca0012_cruise"

    # --Default Values------------------------------------------------
    if x_states_default_values is None:
        x_states_default_values = _get_default_values()

    # ----Variables Optimizer---------------------------------------
    x_states_avl = MDO.parseStateVariable(x_states_global,
                                          variables='short',
                                          x_states_default_values=x_states_default_values)

    wingSpan = x_states_avl[0]
    wingSecPercentage = x_states_avl[1]
    wingRootChord = x_states_avl[2]
    wingMiddleChord = x_states_avl[3]
    wingTipChord = x_states_avl[4]

    verticalSpan = x_states_avl[5]
    verticalRootChord = x_states_avl[6]
    verticalTipChord = x_states_avl[7]
    verticalXPosition = x_states_avl[8]

    fuselageLength = x_states_avl[9]
    fuselageDiameter = 0.18

    if os.environ["DEBUG"] == 'yes':
        print(f"wingSpan: {wingSpan}")
        print(f"wingSecPercentage: {wingSecPercentage}")
        print(f"wingRootChord: {wingRootChord}")
        print(f"wingMiddleChord: {wingMiddleChord}")
        print(f"wingTipChord: {wingTipChord}")
        print(f"verticalSpanAVL: {verticalSpan}")
        print(f"verticalRootChord: {verticalRootChord}")
        print(f"verticalTipChord: {verticalTipChord}")
        print(f"verticalXPosition: {verticalXPosition}")
        print(f"fuselageLength: {fuselageLength}")
        print(f"fuselageDiameter: {fuselageDiameter}")


    # endPlateTipChord = 0.4

    wingSecPosition = wingSpan / 2 * wingSecPercentage
    wingPosSec = wingSpan / 2 * (1 - wingSecPercentage)

    # ----Config CG---------------------------------------
    # Priority order: smFixed > cgFixed
    cgFixed = None
    smFixedPercent = 10  # In percentage  # TODO: Create variablet to static margin
    # ----Parser to dict---------------------------------------
    stateVariables, controlVariables, avlMandatoryCases, avlCases, engineInfo, missionProfile = MDO.set_state_variables(
        wingRootChord=wingRootChord, wingAirfoil=wingAirfoil, wingMiddleChord=wingMiddleChord,
        wingSecPosition=wingSecPosition, wingTipChord=wingTipChord, wingPosSec=wingPosSec,
        horizontalRootChord=None,
        horizontalXPosition=None, verticalXPosition=verticalXPosition,
        horizontalTipChord=None,
        horizontalSpan=None, verticalRootChord=verticalRootChord, verticalTipChord=verticalTipChord,
        verticalSpan=verticalSpan, stabAirfoil=stabAirfoil,
        fuselageLength=fuselageLength, fuselageDiameter=fuselageDiameter
    )

    # ---- Aircraft Info Class ----------------------------------------
    aircraftInfo = AircraftInfo(stateVariables, controlVariables, engineInfo=engineInfo, optimizationVariables=x_states_global)

    # ---- Aircraft Neutral Point Calc ----------------------------------------
    if smFixedPercent is not None:
        results = MDO.avlMain(aircraftInfo, avlMandatoryCases, verticalType=verticalType)
        aircraftInfo.xNeutralPoint = (results['NeutralPoint_0']['StabilityDerivatives']['Xnp']
                                      + results['NeutralPoint_1']['StabilityDerivatives']['Xnp'])/2
        aircraftInfo.adjustCG(cgFixed=None, smFixedPercent=smFixedPercent)
    else:
        aircraftInfo.adjustCG(cgFixed=cgFixed, smFixedPercent=None)

    # ---- Avl -----------------------------------------
    results = MDO.avlMain(aircraftInfo, avlCases, verticalType=verticalType)

    # ---- Results -----------------------------------------
    output_dict = MDO.mainResults(results=results, aircraftInfo=aircraftInfo, avlCases=avlCases,
                                  missionProfile=missionProfile, logger=logger)

    return pd.DataFrame(output_dict, index=[0])


def _get_default_values():
    x_states_default_values = {
        'aspectRatio': 7.07,
        'wingSecPercentage': 0.5,
        'wingArea': 2.15,
        'taperRatio1': 1,
        'taperRatio2': 1,
        'aspectRatioV': 3.29,  # AR from top view
        'areaV': 0.41535,  # Area from top view
        'taperV': 1,
        'posXV': 2.05,
        'fuselageLength': 1.83
    }

    return x_states_default_values


if __name__ == '__main__':
    # ----Process Time--------------------------------------------
    startTime = time.time()

    # ----logging--------------------------------------------
    logger = MDO.createLog(name="main")
    logger.info("------------------BEGIN------------------")

    # ----Config ----------------------------------------------
    MDO.parseConfig("outputsConfig.cfg")

    x_states_global = {  # projeto ótimo final
        'aspectRatio': 1.1836851520621035*10,
        'wingSecPercentage': 0.6828271627065576,
        'wingArea': 0.479545353002881*5,
        'taperRatio1': 0.7503373812423733,
        'taperRatio2': 0.4526662366887399,
        'aspectRatioV': 0.8357522085631572*5,  # AR from top view
        'areaV': 0.32051602780323585,  # Area from top view
        'taperV': 0.31408649182402026,
        'posXV': 0.49818264232832843*5,
        'fuselageLength': 0.16042898056803084*5
    }

    main(x_states_global, x_states_default_values=_get_default_values())

    # ---- Time-----------------------------------------
    print(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info("------------------END------------------")
