import os
from configparser import ConfigParser
import MDO
import matplotlib.pyplot as plt
import math

config = ConfigParser()
config.read(os.path.join("outputsConfig.cfg"))


def mainResults(results=None, aircraftInfo=None, avlCases=None, missionProfile=None, logger=None):
    PRINT = os.getenv('PRINT').lower() == 'yes'
    PLOT = os.getenv('PLOT').lower() == 'yes'

    output_dict = {}

    if PRINT:
        print("------------------------------")

    # ---- Neutral Point ------------------------------------------
    if 'y' in config['output']['NEUTRAL_POINT'].lower():
        MDO.stability.getNeutralPoint(results, aircraftInfo)
        if PRINT:
            print("Neutral Point: ", round(aircraftInfo.xNeutralPoint, 4))
            print(f"SM: {round(aircraftInfo.staticMargin, 2)} %")

        output_dict['neutral_point'] = aircraftInfo.xNeutralPoint
        output_dict['static_margin'] = aircraftInfo.staticMargin

    # ---- Deflections Check --------------------------------------
    if 'y' in config['output']['DEFLECTIONS'].lower():
        deflections = MDO.Deflections(results, aircraftInfo.controlVariables)
        if PRINT:
            print("Deflections:", deflections.cruise)

        output_dict['deflection_cruise_aileron'] = deflections.cruise['aileron']
        output_dict['deflection_cruise_elevator'] = deflections.cruise['elevator']
        output_dict['deflection_cruise_rudder'] = deflections.cruise['rudder']
        output_dict['deflection_cruise_flap'] = deflections.cruise['flap']

    # ---- Polar --------------------------------------------------
    if 'y' in config['output']['POLAR'].lower():
        [aircraftInfo.cD0, aircraftInfo.cD1, aircraftInfo.k, aircraftInfo.dataPolar] = MDO.polar(results, aircraftInfo)
        if PRINT:
            print("Polar:", round(aircraftInfo.cD0, 4), round(aircraftInfo.cD1, 4), round(aircraftInfo.k, 4))
        if PLOT:
            MDO.plotPolar(aircraftInfo)

        output_dict['cd0'] = aircraftInfo.cD0
        output_dict['cd1'] = aircraftInfo.cD1
        output_dict['cd2'] = aircraftInfo.k

    # ---- Stall --------------------------------------------------
    if 'y' in config['output']['STALL'].lower() \
            or 'y' in config['output']['TAKEOFF'].lower():  # TODO: Improve Clmax for takeOff
        MDO.stall(results, aircraftInfo)
        if PRINT:
            print("Wing Stall: ", round(aircraftInfo.alphaStallWing, 1), "deg at ",
                  round(2 * aircraftInfo.stallPositionWing / aircraftInfo.wing.span * 100, 2), "% of wing")
            print(f"CL Max aircraft: {round(aircraftInfo.cLMax, 2)}")
        if PLOT:
            MDO.plotStall(aircraftInfo)
            MDO.plotliftDistribution(results, aircraftInfo, avlCases=avlCases)

        output_dict['alphaStallWing'] = aircraftInfo.alphaStallWing
        output_dict['stallPositionWing'] = 2 * aircraftInfo.stallPositionWing / aircraftInfo.wing.span * 100

    # ---- Range (Raymer)------------------------------------------
    if 'y' in config['output']['RANGE'].lower():
        rangeCruise = MDO.rangeCruise(aircraftInfo.engineInfo['engineFC'], avlCases, aircraftInfo)
        if PRINT:
            print(f"Range Brequet: {round(rangeCruise, 1)}")

    # ---- Thrust ---------------------------------
    if 'y' in config['output']['THRUST'].lower() \
            or 'y' in config['output']['TAKEOFF'].lower():
        [aircraftInfo.thrust.v0, aircraftInfo.thrust.v1, aircraftInfo.thrust.v2] = MDO.performance.dynamicThrustCurve(
            aircraftInfo.engineInfo, method="actuatorDisk")
        if PRINT:
            print(f"Thrust: {round(aircraftInfo.thrust.v0, 2)}, {round(aircraftInfo.thrust.v1, 2)}, {round(aircraftInfo.thrust.v2, 2)}")

    # ---- Take Off ---------------------------------
    if 'y' in config['output']['TAKEOFF'].lower():
        if "takeOffRun" in avlCases:
            [aircraftInfo.cDRunAvl, cDParasite, aircraftInfo.cDRun, aircraftInfo.cLRun] = MDO.getRun(results,
                                                                                                     aircraftInfo)
            aircraftInfo.alphaRun = results["trimmed"]["Totals"]["Alpha"]
            # mission['takeOffRun']["alpha"] = aircraftInfo.alphaRun
            [runway, speedTakeOff, timeTakeOff] = MDO.performance.takeOffRoll(aircraftInfo, dt=0.01, nsteps=15000)
            aircraftInfo.weight.fuelTakeOff = timeTakeOff * (
                    aircraftInfo.engine.consumptionMaxLperH * aircraftInfo.engine.fuelDensity / 3600) * 9.8
            if PRINT:
                print(f"Aircraft TOW: {round(aircraftInfo.weight.MTOW / 9.81, 3)} kg")
                print(f"Runway Length: {round(runway, 3)} m")
                print(f"Take Off Speed: {round(speedTakeOff, 2)} m/s")
                print(f"Time TakeOff: {round(timeTakeOff, 2)} s")
                print(f"Fuel mass TakeOff: {round(aircraftInfo.weight.fuelTakeOff / 9.8, 1)} kg")
                print(f"CD Run AVL: {round(aircraftInfo.cDRunAvl, 5)}")
                print(f"CD Run Total: {round(aircraftInfo.cDRun, 5)}")
                print(f"Alpha Run: {round(aircraftInfo.alphaRun, 3)} º")

            output_dict['weightEmpty'] = aircraftInfo.weight.empty
            output_dict['mtow'] = aircraftInfo.weight.MTOW
            output_dict['runway'] = runway
            output_dict['speedTakeOff'] = speedTakeOff
            output_dict['timeTakeOff'] = timeTakeOff
            output_dict['fuelTakeOff'] = aircraftInfo.weight.fuelTakeOff
            output_dict['cDRunAvl'] = aircraftInfo.cDRunAvl
            output_dict['cDRun'] = aircraftInfo.cDRun
            output_dict['alphaRun'] = aircraftInfo.alphaRun

    # ---- Descent ---------------------------------
    if 'y' in config['output']['DESCENT']:
        MDO.descentFuel(aircraftInfo=aircraftInfo,
                        heightInitial=missionProfile['cruise']['altitude'],
                        heightFinal=missionProfile['descent']['endAltitude'],
                        rateOfDescent=missionProfile['descent']['descentRate'],
                        nSteps=missionProfile['descent']['nSteps'],
                        logger=logger)

        if PRINT:
            print(f"fuel descent: {round(aircraftInfo.weight.fuelDescent / 9.8, 1)} kg")
            print(f"time descent: {round(aircraftInfo.performance.descent.time / 60, 1)} min")

        output_dict['fuelDescent'] = aircraftInfo.weight.fuelDescent
        output_dict['descentTime'] = aircraftInfo.performance.descent.time

    # ---- Climb ---------------------------------
    if 'y' in config['output']['CLIMB'].lower():
        MDO.climbFuel(aircraftInfo=aircraftInfo,
                      heightInitial=missionProfile['climb']['initialAltitude'],
                      heightFinal=missionProfile['climb']['endAltitude'],
                      rateOfClimb=missionProfile['climb']['climbRate'],
                      nSteps=missionProfile['climb']['nSteps'],
                      logger=logger)
        if PRINT:
            print(f"Fuel Climb: {round(aircraftInfo.weight.fuelClimb / 9.8, 1)} kg")
            print(f"Time Climb: {round(aircraftInfo.performance.climb.time / 60, 1)} min")

        output_dict['fuelClimb'] = aircraftInfo.weight.fuelClimb
        output_dict['timeClimb'] = aircraftInfo.performance.climb.time

    # ---- Cruise ---------------------------------
    if 'y' in config['output']['CRUISE'].lower():
        fuelKg = (aircraftInfo.weight.fuel - aircraftInfo.weight.fuelTakeOff - aircraftInfo.weight.fuelClimb) / 9.8
        fuelDescentKg = (aircraftInfo.weight.fuelReserve + aircraftInfo.weight.fuelDescent) / 9.8

        MDO.cruise(aircraftInfo=aircraftInfo,
                   avlCases=avlCases,
                   fuelKg=fuelKg,
                   fuelDescentKg=fuelDescentKg,
                   nSteps=missionProfile['cruise']['nSteps'],
                   logger=logger)
        if PRINT:
            print(
                f"Range Cruise: {round(aircraftInfo.performance.cruise.range / 1000, 2)} km, with {round(fuelKg - fuelDescentKg, 1)} kg of fuel")
            print(
                f"Time Cruise: {math.floor(aircraftInfo.performance.cruise.time / 3600)} h e {round(aircraftInfo.performance.cruise.time / 60 - math.floor(aircraftInfo.performance.cruise.time / 3600) * 60, 1)} min")

        output_dict['cruiseRange'] = aircraftInfo.performance.cruise.range / 1000
        output_dict['timeClimb'] = aircraftInfo.performance.climb.time
    # ---- Lift Distribution ----------------------
    if 'y' in config['output']['LIFT_DIST'].lower():
        MDO.liftDistNewton(results, avlCases)

    # ---- Hinge Moment ---------------------------
    if 'y' in config['output']['TOTAL_HINGE_MOMENT'].lower():
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

    # ---- Plot Mission Profile ---------------------------
    if 'y' in config['output']['CRUISE'].lower() and \
            'y' in config['output']['CLIMB'].lower() and \
            'y' in config['output']['DESCENT'].lower():

        rangeClimb = aircraftInfo.performance.climb.range
        rangeCruise = aircraftInfo.performance.cruise.range
        rangeDescent = aircraftInfo.performance.descent.range
        rangeAll = rangeDescent + rangeCruise + rangeDescent

        if PLOT:
            missionPlot = [[0, runway / 1000, rangeClimb / 1000, (rangeClimb + rangeCruise) / 1000,
                            rangeAll / 1000],
                           [0, 0, 1500, 1500, 0]]

            plt.plot(missionPlot[0], missionPlot[1])
            plt.xlabel("Range (km)")
            plt.ylabel("Altitude (m)")
            plt.show()

        if PRINT:
            print(f"Range flight: {round( rangeAll/ 1000, 1)} km")

        output_dict['range_all'] = rangeAll / 1000

    # ---- Check CG Positionable ---------------------------
    if 'y' in config['output']['CG_POSITIONABLE'].lower():
        cgPositionable, allElseCgPercentFuselage= MDO.cgPositionable(aircraftInfo)

        if PRINT:
            print(f"Cg Positionable: {cgPositionable}, at {allElseCgPercentFuselage} of fuselage")

        output_dict['cgPostionable'] = cgPositionable
        output_dict['allElseCgPercentFuselage'] = allElseCgPercentFuselage

    # ---- Check CG Positionable ---------------------------
    MDO.checkOutputValues(output_dict, aircraftInfo)

    # ---- End ---------------------------
    if PRINT:
        print("------------------------------")

    return output_dict
