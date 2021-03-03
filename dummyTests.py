import MDO

stateVariables = {
    "wing": {
        "root": {
            "chord": 0.9,
            "aoa": 0,
            "x": 0,
            "y": 0,
            "z": 0,
            "airfoil": MDO.airfoils.AirfoilData("n2414")
        },
        "middle": {
            "chord": 0.7,
            "b": 3.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("n2414")
        },
        "tip": {
            "chord": 0.675,
            "b": 1.6,
            "sweepLE": 0,
            "aoa": 0,
            "dihedral": 0,
            "airfoil": MDO.airfoils.AirfoilData("n2414")
        },
    }
}

print(stateVariables["wing"]["root"]["airfoil"].name)


