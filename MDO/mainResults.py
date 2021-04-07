import os
from configparser import ConfigParser
import MDO
import matplotlib.pyplot as plt

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
            aircraftInfo.weight.fuelTakeOff = timeTakeOff * (aircraftInfo.engine.consumptionMaxLperH * \
                                                             aircraftInfo.engine.fuelDensity / 3600) * 9.8
            if PRINT:
                print(f"Aircraft TOW: {aircraftInfo.weight.MTOW / 9.81} kg")
                print(f"Runway Length: {round(runway, 3)} m")
                print(f"Take Off Speed: {speedTakeOff} m/s")
                print(f"Time TakeOff: {timeTakeOff} s")
                print(f"Fuel mass TakeOff: {round(aircraftInfo.weight.fuelTakeOff / 9.8, 1)} kg")
                print(f"CD Run AVL: {aircraftInfo.cDRunAvl}")
                print(f"CD Run Total: {aircraftInfo.cDRun}")
                print(f"Alpha Run: {round(aircraftInfo.alphaRun, 4)} º")
    # ---- Descent ---------------------------------
    if 'y' in config['output']['DESCENT']:
        aircraftInfo.weight.fuelDescent, timeDescent, xDistDescent = MDO.descentFuel(aircraftInfo=aircraftInfo,
                                                                       heightInitial=1500,
                                                                       heightFinal=0,
                                                                       rateOfDescent=1,
                                                                       nSteps=20)

        if PRINT:
            print(f"fuel descent: {round(aircraftInfo.weight.fuelDescent / 9.8, 1)} kg")
            print(f"time descent: {round(timeDescent / 60, 1)} min")

    # ---- Climb ---------------------------------
    if 'y' in config['output']['CLIMB'].lower():
        aircraftInfo.weight.fuelClimb, climbTime, xDistClimb = MDO.climbFuel(aircraftInfo=aircraftInfo,
                                                                             heightInitial=0,
                                                                             heightFinal=1500,
                                                                             rateOfClimb=1,
                                                                             nSteps=20)
        if PRINT:
            print(f"Fuel Climb: {round(aircraftInfo.weight.fuelClimb / 9.8, 1)} kg")
            print(f"Time Climb: {round(climbTime / 60, 1)} min")

    # ---- Cruise ---------------------------------
    if 'y' in config['output']['CRUISE'].lower():
        fuelKg = (aircraftInfo.weight.fuel - aircraftInfo.weight.fuelTakeOff - aircraftInfo.weight.fuelClimb) / 9.8
        fuelDescentKg = (aircraftInfo.weight.fuelReserve + aircraftInfo.weight.fuelDescent) / 9.8

        rangeCruise, timeCruise = MDO.cruise(aircraftInfo=aircraftInfo,
                                             mission=mission,
                                             fuelKg=fuelKg,
                                             fuelDescentKg=fuelDescentKg,
                                             nSteps=2)
        if PRINT:
            print(
                f"Range Cruise: {round(rangeCruise / 1000, 2)} km, with {round(fuelKg - fuelDescentKg, 1)} kg of fuel")
            print(
                f"Time Cruise: {round(timeCruise / 3600, 0)} h e {round(timeCruise / 60 - round(timeCruise / 3600, 0) * 60, 1)} min")

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

    # ---- Plot Mission Profile ---------------------------
    if 1:
        missionPlot = [[0, runway/1000, xDistClimb/1000, (xDistClimb + rangeCruise)/1000, (xDistClimb + rangeCruise + xDistDescent)/1000],
                       [0, 0, 1500, 1500, 0]]

        plt.plot(missionPlot[0], missionPlot[1])
        plt.xlabel("Range (km)")
        plt.ylabel("Altitude (m)")
        plt.show()
