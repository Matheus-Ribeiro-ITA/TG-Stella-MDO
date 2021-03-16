import os
from configparser import ConfigParser

import MDO


config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))


def mainResults(results=None, aircraftInfo=None, mission=None):
    PRINT = os.getenv('PRINT').lower() == 'yes'
    PLOT = os.getenv('PLOT').lower() == 'yes'
    if PRINT:
        print("------------------------------")

    # ---- Neutral Point ------------------------------------------
    if 'y' in config['output']['NEUTRAL_POINT'].lower():
        MDO.stability.getNeutralPoint(results, aircraftInfo)
        if PRINT:
            print("Neutral Point: ", aircraftInfo.xNeutralPoint)
            print(f"EM: {round(aircraftInfo.staticMargin, 2)} %")

    # ---- Deflections Check --------------------------------------
    if 'y' in config['output']['DEFLECTIONS'].lower():
        deflections = MDO.Deflections(results, aircraftInfo.controlVariables)
        if PRINT:
            print("Deflections:", deflections.cruise)

    # ---- Polar --------------------------------------------------
    if 'y' in config['output']['POLAR'].lower():
        [aircraftInfo.cD0, aircraftInfo.cD1, aircraftInfo.k, aircraftInfo.dataPolar] = MDO.polar(results, aircraftInfo)
        if PRINT:
            print("Polar:", aircraftInfo.cD0, aircraftInfo.cD1, aircraftInfo.k)
        if PLOT:
            MDO.plotPolar(aircraftInfo)

    # ---- Stall --------------------------------------------------
    if 'y' in config['output']['STALL'].lower() \
            or 'y' in config['output']['TAKEOFF'].lower():  # TODO: Improve Clmax for takeOff
        MDO.stall(results, aircraftInfo)
        if PRINT:
            print("Wing Stall: ", round(aircraftInfo.alphaStallWing, 1), "deg at ", round(2*aircraftInfo.stallPositionWing/aircraftInfo.wingSpan*100, 2), "% of wing")
            print(f"CL Max aircraft: {aircraftInfo.cLMax}")
        if PLOT:
            MDO.plotStall(aircraftInfo)
            MDO.plotliftDistribution(results, aircraftInfo)

    # ---- Range ------------------------------------------
    if 'y' in config['output']['RANGE'].lower():
        rangeCruise = MDO.rangeCruise(aircraftInfo.engineInfo['engineFC'], mission, aircraftInfo)
        if PRINT:
            print(f"Range: {rangeCruise}")

    # ---- Thrust ---------------------------------
    if 'y' in config['output']['THRUST'].lower() \
            or 'y' in config['output']['TAKEOFF'].lower():
        [aircraftInfo.thrustV0, aircraftInfo.thrustV1, aircraftInfo.thrustV2] = MDO.performance.dynamicThrustCurve(aircraftInfo.engineInfo, method="actuatorDisk")
        if PRINT:
            print(f"Thrust: {aircraftInfo.thrustV0}, {aircraftInfo.thrustV1}, {aircraftInfo.thrustV2}")

    # ---- Take Off ---------------------------------
    if 'y' in config['output']['TAKEOFF'].lower():
        if "takeOffRun" in mission:
            [aircraftInfo.cDRunAvl, cDParasite, aircraftInfo.cDRun, aircraftInfo.cLRun] = MDO.getRun(results, aircraftInfo)
        aircraftInfo.alphaRun = results["trimmed"]["Totals"]["Alpha"]
        # mission['takeOffRun']["alpha"] = aircraftInfo.alphaRun
        [runway, speedTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)
        if PRINT:
            print(f"Aircraft TOW: {aircraftInfo.MTOW / 9.81} kg")
            print(f"Runway Length: {runway} m")
            print(f"Take Off Speed: {speedTakeOff} m/s")
            print(f"CD Run AVL: {aircraftInfo.cDRunAvl}")
            print(f"CD Run Total: {aircraftInfo.cDRun}")
            print(f"Alpha Run: {aircraftInfo.cDRun}")

    # ---- Cruise ---------------------------------
    if 'y' in config['output']['CRUISE'].lower():
        aircraftInfo.cDCruiseAvl = results["trimmed"]["Totals"]["CDtot"]
        aircraftInfo.dragCruiseAvl = 1 / 2 * 1.2 * aircraftInfo.cDCruiseAvl * mission['cruise'][
            'vCruise'] ** 2 * aircraftInfo.wingArea
        if PRINT:
            print(f"Cd Cruise AVL: {aircraftInfo.cDCruiseAvl}")
            print(f"Drag Cruise AVL: {aircraftInfo.dragCruiseAvl} N")

    # ---- Lift Distribution ---------------------------------
    if 'y' in config['output']['LIFT_DIST'].lower():
        MDO.liftDistNewton(results, mission)

    if PRINT:
        print("------------------------------")