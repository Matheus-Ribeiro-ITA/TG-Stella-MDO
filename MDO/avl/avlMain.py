import os
import MDO.avl as avl
import json


def avlMain(aircraftInfo, mission, verticalType="conventional"):
    """
    # Description:
        Run all AVL related processes.

    ## Params:
        aircraftInfo [Instance]: Aircraft info class object.
        mission [json]: Mission details.

    ## Returns:
        results [json]: AVL results.
    """
    # -----Avl Run-----------------------------------------
    results = avl.avlRun(
        geometry=avl.avlGeoBuild(aircraftInfo.stateVariables,
                                 aircraftInfo.controlVariables,
                                 verticalType=verticalType),
        cases=avl.avlRunBuild(mission,
                              aircraftInfo)
    )
    print("Aee")
    # -----Save results-----------------------------------------
    if 'y' in os.getenv('DEBUG').lower():
        with open("aircraft/results.json", "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)
            file.close()

    return results
