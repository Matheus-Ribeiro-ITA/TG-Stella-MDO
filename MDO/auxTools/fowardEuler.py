import numpy as np

def forward_euler(q0, qd, dt=0.01, nsteps=6000):
    stts = [q0]
    ts = [0.0]

    for _ in range(nsteps):
        qdt = qd(stts[-1])
        q = stts[-1] + qdt * dt

        stts.append(q)
        ts.append(ts[-1] + dt)

    return ts, np.vstack(stts)