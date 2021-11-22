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
        fuselageLength=fuselageLength, fuselageDiameter=fuselageDiameter
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
    # areaStab = 1.17*sqrt(2)*0.355 = 0.587 = 0.41535 sem sqrt(2) == topview
    # arStab = b_stab_view_to^2/areaStab = 1.17^2/0.587 = 2.33 or 3.29 sem sqrt(2)
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

    #
    # x_states_global = {  # Otimização mono-objetiva de alcance
    #     'aspectRatio': 13.9314,
    #     'wingSecPercentage': 0.675,
    #     'wingArea': 0.20076*5,
    #     'taperRatio1':  0.725,
    #     'taperRatio2': 0.406,
    #     'aspectRatioV': 0.334*5,  # AR from top view
    #     'areaV': 0.321,  # Area from top view
    #     'taperV': 0.316,
    #     'posXV':  0.433*5,
    #     'fuselageLength': 0.1680*5
    # }

    # x_states_global = {  # Otimização mono-objetiva de tamanho de pista
    #     'aspectRatio': 1.3840681241377664*10,
    #     'wingSecPercentage': 0.5222421951345299,
    #     'wingArea': 0.5977726509080452*5,
    #     'taperRatio1':  0.91038399497762,
    #     'taperRatio2': 0.37506074830000413,
    #     'aspectRatioV': 0.32783229631*5,  # AR from top view
    #     'areaV': 1.3359631,  # Area from top view
    #     'taperV': 0.48973280,
    #     'posXV':  0.4928859*5,
    #     'fuselageLength': 0.1986*5
    # }
    # x_states_global = {  # projeto ótimo final
    #     'aspectRatio': 13.9,
    #     'wingSecPercentage': 0.67,
    #     'wingArea': 2.47,
    #     'taperRatio1': 0.75,
    #     'taperRatio2': 0.31,
    #     'aspectRatioV': 4.55,  # AR from top view
    #     'areaV': 0.306,  # Area from top view
    #     'taperV': 0.32,
    #     'posXV': 2.5,
    #     'fuselageLength': 0.80
    # }
    # 44, 0.8091479136428312, 0.6157898823230807, 0.5957155623044272, 0.3909394837252448, 0.8135191602727404, 0.6190261723993528, 0.3230627180986147, 0.9572100781787451, 0.45569767511203, 0.16712699841702863, -10.97606990307842, 0.2079895728158605
    # 45, 0.8107805061937362, 0.6157898823230807, 0.5957155623044272, 0.3909394837252448, 0.8135191602727404, 0.6190261723993528, 0.3230627180986147, 0.884711854135352, 0.45569767511203, 0.16712847942164183, -2.5879800399001556, 0.20798775505789635


    # x_states_global = {  # Aeronave estranha
    #     'aspectRatio': 0.8091479136428312*10,
    #     'wingSecPercentage': 0.6157898823230807,
    #     'wingArea': 0.5957155623044272*5,
    #     'taperRatio1': 0.3909394837252448,
    #     'taperRatio2': 0.8135191602727404,
    #     'aspectRatioV': 0.6190261723993528*5,  # AR from top view
    #     'areaV': 0.3230627180986147,  # Area from top view
    #     'taperV': 0.9572100781787451,
    #     'posXV':  0.45569767511203*5,
    #     'fuselageLength': 0.16712699841702863*5
    # }

    # x_states_global = {  # Aeronave estranha
    #     'aspectRatio': 0.8107805061937362*10,
    #     'wingSecPercentage': 0.6157898823230807,
    #     'wingArea': 0.5957155623044272*5,
    #     'taperRatio1': 0.3909394837252448,
    #     'taperRatio2': 0.8135191602727404,
    #     'aspectRatioV': 0.6190261723993528*5,  # AR from top view
    #     'areaV': 0.3230627180986147,  # Area from top view
    #     'taperV': 0.9572100781787451,
    #     'posXV':  0.45569767511203*5,
    #     'fuselageLength': 0.16712699841702863*5
    # }

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

    #
    # x_states_global = {
    #     'aspectRatio': 7.07,
    #     'wingSecPercentage': 0.5,
    #     'wingArea': 2.15,
    #     'taperRatio1': 1,
    #     'taperRatio2': 1,
    #     'aspectRatioV': 3.29,  # AR from top view
    #     'areaV': 0.41535,  # Area from top view
    #     'taperV': 1,
    #     'posXV': 2.05,
    #     'fuselageLength': 1.83
    # }

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
