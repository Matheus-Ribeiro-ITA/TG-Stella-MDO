from MDO.auxTools import atmosphere
import numpy as np
import matplotlib.pyplot as plt


def flightEnvelop(aircraftInfo, maxheight=4*10**3):
    mtow = aircraftInfo.weight.MTOW
    wingArea = aircraftInfo.wing.area
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k
    t0 = aircraftInfo.thrust.v0
    t1 = aircraftInfo.thrust.v1
    t2 = aircraftInfo.thrust.v2
    cLMax = aircraftInfo.cLMax
    slopeAltitude = aircraftInfo.engineInfo["altitudeCorrection"]['slope']

    ceilingHeight = 0
    vMin = []

    nLoad = 2.5
    rho0 = 1.2
    vSeaStruct = np.sqrt(2*nLoad*mtow/(cLMax*wingArea*rho0))
    vMaxStruct = []
    vMinEngine = []
    vMaxEngine = []

    heights = np.linspace(1, maxheight, 150)
    velocities = np.linspace(10, 50, 100)
    for height in heights:
        T, p, rho, mi = atmosphere(height)
        gotVmin = False
        gotVmax = False
        gotCeiling = False
        efficiencyAltitude = 1 + slopeAltitude * height

        for velocity in velocities:
            cL = 2*mtow/(velocity**2*wingArea*rho)
            cD = cD0 + cD1*cL + cD2*cL**2
            drag = 1/2*rho*velocity**2*wingArea*cD
            thrust = (t0 + t1*velocity + t2*velocity**2)*efficiencyAltitude
            rateOffClimb = (thrust - drag)/mtow * velocity

            if drag < thrust and not gotVmin:
                vMinEngine.append((height, velocity))
                gotVmin = True

            if drag > thrust and gotVmin and not gotVmax:
                vMaxEngine.append((height, velocity))
                gotVmax = True

            if rateOffClimb > 100*0.00508:  # UAV Gundlach page 358
                ceilingHeight = height
                gotCeiling = True

            if gotCeiling and gotVmin and gotVmax:
                break

        vMin.append(np.sqrt(2*mtow/(cLMax*wingArea*rho)))
        vMaxStruct.append(vSeaStruct*np.sqrt(rho0/rho))

    return Envelope(heights, ceilingHeight, vMin, vMaxStruct, vMinEngine, vMaxEngine)


def plotDragThrust(aircraftInfo, height=1500):
    mtow = aircraftInfo.weight.MTOW
    wingArea = aircraftInfo.wing.area
    cD0 = aircraftInfo.cD0
    cD1 = aircraftInfo.cD1
    cD2 = aircraftInfo.k
    t0 = aircraftInfo.thrust.v0
    t1 = aircraftInfo.thrust.v1
    t2 = aircraftInfo.thrust.v2
    slopeAltitude = aircraftInfo.engineInfo["altitudeCorrection"]['slope']
    efficiencyAltitude = 1 + slopeAltitude*height

    T, p, rho, mi = atmosphere(height)

    drags = []
    thrusts = []
    velocities = []

    for velocity in range(10, 50, 1):
        cL = 2 * mtow / (velocity ** 2 * wingArea * rho)
        cD = cD0 + cD1 * cL + cD2 * cL ** 2
        drags.append(1 / 2 * rho * velocity ** 2 * wingArea * cD)
        thrusts.append((t0 + t1 * velocity + t2 * velocity ** 2)*efficiencyAltitude)
        velocities.append(velocity)

    plt.plot(velocities, drags, label='Drag')
    plt.plot(velocities, thrusts, label='Thrust')
    plt.legend()
    plt.xlabel('Velocity (m/s)')
    plt.ylabel('Force (N)')
    plt.ylim([0, 400])
    plt.show()

    return


class Envelope:
    def __init__(self, heights, ceilingHeight, vMin, vMaxStruct, vMinEngine, vMaxEngine):
        self.heights = heights
        self.ceiling = ceilingHeight
        self.vMin = vMin
        self.vMaxStruct = vMaxStruct
        self.vMinEngine = list(zip(*vMinEngine))
        self.vMaxEngine = list(zip(*vMaxEngine))

    def plot(self):
        plt.plot([0, 50], [self.ceiling, self.ceiling], label='Service Ceiling')
        plt.plot(self.vMin, self.heights, label='V Stall')
        plt.plot(self.vMaxStruct, self.heights, label='V Max Struct')
        plt.plot(self.vMinEngine[1], self.vMinEngine[0], label='V Min Engine')
        plt.plot(self.vMaxEngine[1], self.vMaxEngine[0], label='V Max Engine')
        plt.legend()
        plt.xlabel('Velocity (m/s)')
        plt.ylabel('Height (m)')
        plt.show()
        return


