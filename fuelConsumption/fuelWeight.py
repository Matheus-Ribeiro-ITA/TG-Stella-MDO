import numpy as np

# def fuelWeight(aircraft, W0_guess, CD0_cruise, K_cruise, altitude_cruise, Mach_cruise, range_cruise, cCruise,
#                 loiter_time, CD0_altcruise, K_altcruise, altitude_altcruise, Mach_altcruise, range_altcruise,
#                 C_altcruise):
def fuelWeight(mission):
    """
    This module computes the fuel contribution to the Maximum Takeoff Weight (MTOW). Some of the fuel fractions
can be estimated using the historical data shown in Fig. 2.
    """
    mf = 1.0
    fig2Value = {
        'engineValue': 0.990,
        'taxi': 0.990,
        'takeOff': 0.995,
        'climb': 0.980,
        "descent": 0.990,
        "landing": 0.992
    }  # Check figure 2 for correct value

    for phase in fig2Value:
        mf = mf * fig2Value[phase]

    mfFixed = mf  # Before any computation regarding the cruise phase, we need to store the current fuel fraction for posterior calculations

    def ff(range, c):
        v = mission["cruise"]["vCruise"]
        cl =
        cd =
        ffOutput = np.exp(-range * c * cd / (v * cl))  # fuel fraction brequet equation
        return ffOutput

    def ff_loiter():
        liftToDrag = 1 / (2 * np.sqrt(CD0_cruise * K_cruise))
        cLoiter = 0.8 * cCruise
        ffLoiter = np.exp(-loiter_time * cLoiter / liftToDrag)  # fuel fraction brequet equation
        return ffLoiter

    mf = mf * ff(altitude_cruise, Mach_cruise, CD0_cruise, K_cruise, range_cruise, cCruise)
    mf = mf * ff_loiter()
    mf = mf * fig2Value["descent"]
    mf = mf * ff(altitude_altcruise, Mach_altcruise, CD0_altcruise, K_altcruise, range_altcruise, C_altcruise)
    mf = mf * fig2Value["landing"]  # 1.3.12

    wf = 1.06 * (1 - mf) * W0_guess

    return wf, mfFixed