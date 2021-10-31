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
    wingAirfoil = "naca4415_cruise"  # Shadow 200 Airfoil

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


    # endPlateTipChord = 0.4

    wingSecPosition = wingSpan / 2 * wingSecPercentage
    wingPosSec = wingSpan / 2 * (1 - wingSecPercentage)

    # ----Config CG---------------------------------------
    # Priority order: smFixed > cgFixed
    cgFixed = None
    smFixedPercent = 10  # In percentage
    # ----Parser to dict---------------------------------------
    stateVariables, controlVariables, avlMandatoryCases, avlCases, engineInfo, missionProfile = MDO.set_state_variables(
        wingRootChord=wingRootChord, wingAirfoil=wingAirfoil, wingMiddleChord=wingMiddleChord,
        wingSecPosition=wingSecPosition, wingTipChord=wingTipChord, wingPosSec=wingPosSec,
        horizontalRootChord=None,
        horizontalXPosition=None, verticalXPosition=verticalXPosition,
        horizontalTipChord=None,
        horizontalSpan=None, verticalRootChord=verticalRootChord, verticalTipChord=verticalTipChord,
        verticalSpan=verticalSpan, stabAirfoil=stabAirfoil,
        fuselageLength=fuselageLength
    )

    # ---- Aircraft Info Class ----------------------------------------
    aircraftInfo = AircraftInfo(stateVariables, controlVariables, engineInfo=engineInfo, optimizationVariables=x_states_global)

    # ---- Aircraft Neutral Point Calc ----------------------------------------
    if smFixedPercent is not None:
        results = MDO.avlMain(aircraftInfo, avlMandatoryCases, verticalType=verticalType)
        # cL1 = results['NeutralPoint_0']['Totals']['CLtot']
        # cL2 = results['NeutralPoint_1']['Totals']['CLtot']
        # cm1 = results['NeutralPoint_0']['Totals']['Cmtot']
        # cm2 = results['NeutralPoint_1']['Totals']['Cmtot']
        #
        # test = (cm2-cm1)/(cL2 - cL1)
        # aircraftInfo.xNeutralPoint = results['NeutralPoint_0']['StabilityDerivatives']['Xnp']
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

    # Shadow Values
    # cWing = 3.9/7.07 = 0.55
    # areaWing = 3.9^2/7.07 = 2.15

    # b_stab_view_top = 99/330*3.9 = 1.17
    # c_stab_view_top = 62/96*0.55 = 0.355
    # areaStab = 1.17*sqrt(2)*0.355 = 0.587 = 0.41535 sem sqrt(2)
    # arStab = b_stab_view_to^2/ = 1.17^2/0.587 = 2.33 or 3.29 sem sqrt(2)
    # fuselageLength = 3.4*312/580 = 1.83
    # posV = 3.4*350/580 = 2.05
    # fuselageDiam = 3.4*31/580 = 0.18

    # SHADOW 200
    # x_states_global[0] = 7.07  # aspectRatio
    # x_states_global[1] = 0.5  # wingSecPercentage
    # x_states_global[2] = 2.15  # wingArea
    # x_states_global[3] = 1  # taperRatio1
    # x_states_global[4] = 1  # taperRatio2
    # x_states_global[5] = 2.33  # aspectRatioV
    # x_states_global[6] = 0.587  # areaV
    # x_states_global[7] = 1  # taperV
    # x_states_global[8] = 2.05  # posXV
    # x_states_global[9] = 1.83  # fuselageLength

    x_states_global = {
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


    # x_states[0] = 6  # wingSpan = 6
    # x_states[1] = 0.5  # wingSecPercentage = 0.5
    # x_states[2] = 0.68  # wingRootChord = 0.68
    # x_states[3] = 0.35  # wingTipChord = 0.35
    # wingMiddleChord = (x_states[2] + x_states[3]) / 2
    #
    # x_states[4] = 1.5  # horizontalSpan = 1.5
    # x_states[5] = 0.5  # horizontalRootChord = 0.5
    # x_states[6] = 0.5  # horizontalTipChord = 0.5
    # x_states[7] = 2  # horizontalXPosition = 2
    #
    # x_states[8] = 0.8  # verticalSpan = 0.8 Remember that is H vertical
    # x_states[9] = 0.375  # verticalRootChord = 0.375
    # x_states[10] = 0.375  # verticalTipChord = 0.375

    # endPlateTipChord = 0.4  # endPlateTipChord = 0.4

    # wingSecPosition = x_states[0] / 2 * x_states[1]
    # wingPosSec = x_states[0] / 2 * (1 - x_states[1])

    main(x_states_global, x_states_default_values=x_states_default_values)

    # ---- Time-----------------------------------------
    print(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info(f"Process Time: {round((time.time() - startTime), 1)} s")
    logger.info("------------------END------------------")
