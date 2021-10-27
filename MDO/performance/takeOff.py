import numpy as np
from MDO.auxTools import forward_euler


def takeOffRoll(aircraftInfo, mu=0.03, ksafety=1.1, dt=0.01, nsteps=8000):
    rho = 1.225  # TODO:
    CLmax = aircraftInfo.cLMax*1.45  # TODO: Add flap to takeOff

    Sref = aircraftInfo.wing.area
    TOW = aircraftInfo.weight.MTOW

    _polar = lambda CL: aircraftInfo.cD0Run + aircraftInfo.cD1Run * CL + aircraftInfo.kRun * CL ** 2
    _tCurve = lambda velocity: aircraftInfo.thrust.v0 + aircraftInfo.thrust.v1 * velocity \
                               + aircraftInfo.thrust.v2 * velocity ** 2
    W = TOW

    if aircraftInfo.cDRun:
        cLRun = aircraftInfo.cLRun
        cDRun = aircraftInfo.cDRun
    else:
        cLRun = aircraftInfo.cLAlpha0
        cDRun = _polar(cLRun)

    Vstall = np.sqrt(2.0 * W / (Sref * rho * CLmax))

    Vto = Vstall * ksafety
    q0 = np.array([0.0, 0.0])  # state vector, [x, Uinf]t

    def qdot(q):
        Uinf = q[1]

        qdyn = Uinf ** 2 * rho / 2

        L = qdyn * Sref * cLRun
        D = qdyn * Sref * cDRun

        N = (
            W - L if L < W else 0.0
        )
        Fat = N * mu

        FX = _tCurve(Uinf) - Fat - D

        return np.array(
            [
                q[1], FX / (TOW/9.81)
            ]
        )

    ts, qs = forward_euler(q0, qdot, dt=dt, nsteps=nsteps)

    finished_q = False
    for i, q in enumerate(qs):
        if q[1] >= Vto:
            finished_q = True
            return q[0], q[1], i*dt

    if not finished_q:
        qs[-1, 0] = 9000

    timeTakeOff = len(qs[:, 0])*dt
    return qs[-1, 0], qs[-1, 1], timeTakeOff
