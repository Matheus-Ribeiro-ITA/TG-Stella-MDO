import numpy as np

def forward_euler(q0, qd, dt = 0.01, nsteps = 1000):
    stts = [q0]
    ts = [0.0]

    for _ in range(nsteps):
        qdt = qd(stts[-1])
        q = stts[-1] + qdt * dt

        stts.append(q)
        ts.append(ts[-1] + dt)

    return ts, np.vstack(stts)

def takeOffRoll(
    polar = lambda CL : 0.0628 - 0.042 * CL + 0.071 * CL ** 2,
    Tcurve = lambda U: 49.1972 - 0.3894 * U - 0.0184 * U ** 2,
    TOW = 21.2,
    g = 9.81,
    rho = 1.1,
    CLmax = 2.103,
    CL0 = 0.62,
    Sref = 1.31466,
    mu = 0.03,
    ksafety = 1.1,
    dt = 0.01,
    nsteps = 1000
):
    W = TOW * g

    Vstall = np.sqrt(2.0 * W / (Sref * rho * CLmax))
    Vto = Vstall * ksafety

    q0 = np.array([0.0, 0.0]) # state vector, [x, Uinf]t

    def qdot(q):
        CL = CL0
        CD = polar(CL)

        Uinf = q[1]

        qdyn = Uinf ** 2 * rho / 2

        L = qdyn * Sref * CL
        D = qdyn * Sref * CD

        N = (
            W - L if L < W else 0.0
        )
        Fat = N * mu

        FX = Tcurve(Uinf) - Fat - D

        return np.array(
            [
            q[1], FX / TOW
            ]
        )

    ts, qs = forward_euler(q0, qdot, dt = dt, nsteps = nsteps)

    for q in qs:
        if q[1] >= Vto:
            return q[0], q[1]
    
    return qs[-1, 0], qs[-1, 1]
