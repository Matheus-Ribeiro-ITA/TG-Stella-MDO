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
            print("Wing Stall: ", round(aircraftInfo.alphaStallWing, 1), "deg at ",
                  round(2 * aircraftInfo.stallPositionWing / aircraftInfo.wing.span * 100, 2), "% of wing")
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
        [aircraftInfo.thrust.v0, aircraftInfo.thrust.v1, aircraftInfo.thrust.v2] = MDO.performance.dynamicThrustCurve(
            aircraftInfo.engineInfo, method="actuatorDisk")
        if PRINT:
            print(f"Thrust: {aircraftInfo.thrust.v0}, {aircraftInfo.thrust.v1}, {aircraftInfo.thrust.v2}")

    # ---- Take Off ---------------------------------
    if 'y' in config['output']['TAKEOFF'].lower():
        if "takeOffRun" in mission:
            [aircraftInfo.cDRunAvl, cDParasite, aircraftInfo.cDRun, aircraftInfo.cLRun] = MDO.getRun(results,
                                                                                                     aircraftInfo)
        aircraftInfo.alphaRun = results["trimmed"]["Totals"]["Alpha"]
        # mission['takeOffRun']["alpha"] = aircraftInfo.alphaRun
        [runway, speedTakeOff, timeTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)
        maxPowerKw = aircraftInfo.engineInfo['maxPowerHp'] * 0.7457
        massTakeOff = timeTakeOff * (maxPowerKw * aircraftInfo.engineInfo['engineFC']['BSFC'] / 3600)
        if PRINT:
            print(f"Aircraft TOW: {aircraftInfo.weight.MTOW / 9.81} kg")
            print(f"Runway Length: {round(runway, 3)} m")
            print(f"Take Off Speed: {speedTakeOff} m/s")
            print(f"Time TakeOff: {timeTakeOff} s")
            print(f"Fuel mass TakeOff: {round(massTakeOff, 1)} g")
            print(f"CD Run AVL: {aircraftInfo.cDRunAvl}")
            print(f"CD Run Total: {aircraftInfo.cDRun}")
            print(f"Alpha Run: {round(aircraftInfo.alphaRun, 4)} º")

    if 'y' in config['output']['CLIMB'].lower():
        [climbFuel, climbTime] = MDO.climbFuel(aircraftInfo=aircraftInfo,
                                               heightInitial=0,
                                               heightFinal=1500,
                                               rateOfClimb=1,
                                               nSteps=20)
        if PRINT:
            print(f"Fuel Climb: {climbFuel} kg")
            print(f"Time Climb: {climbTime} kg")
    # ---- Cruise ---------------------------------
    if 'y' in config['output']['CRUISE'].lower():
        aircraftInfo.cDCruiseAvl = results["trimmed"]["Totals"]["CDtot"]
        aircraftInfo.dragCruiseAvl = 1 / 2 * 1.2 * aircraftInfo.cDCruiseAvl * mission['cruise'][
            'vCruise'] ** 2 * aircraftInfo.wing.area
        if PRINT:
            print(f"Cd Cruise AVL: {round(aircraftInfo.cDCruiseAvl, 5)}")
            print(f"Drag Cruise AVL: {round(aircraftInfo.dragCruiseAvl, 3)} N")

    # ---- Lift Distribution ----------------------
    if 'y' in config['output']['LIFT_DIST'].lower():
        MDO.liftDistNewton(results, mission)

    # ---- Hinge Moment ---------------------------
    if 'y' in config['output']['HINGE_MOMENT'].lower():
        momentPerPressure = MDO.getHingeMoment(results, aircraftInfo)
        velocity = 20
        rho = 1.2
        moments = [1 / 2 * velocity ** 2 * rho * a for a in momentPerPressure]
        if PRINT:
            momentKgCm = [round(moment, 2) * 10 for moment in moments]
            print(f"[Aileron, Flap, Elevator moments] {momentKgCm} Kg.cm")

    # ---- Flight Envelope ---------------------------
    if 'y' in config['output']['FLIGHT_ENVELOPE'].lower():
        if PLOT:
            envelope = MDO.flightEnvelop(aircraftInfo)
            envelope.plot()

    if PRINT:
        print("------------------------------")
