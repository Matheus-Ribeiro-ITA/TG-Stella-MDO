import avl.avlwrapper as avl


def avlRun(geometry, cases):
    """
    # Description:
        Call the Avl Wrapper and run it with the aircraft object and cases list.

    ## Parameters (Required):
    - geometry [Object]: Avl Wrapper Object.
    - cases [List]: list of case objects.

    ## Returns:
    - results [dict]: dict with results.
    """
    session = avl.Session(geometry=geometry, cases=cases)
    results = session.run_all_cases()

    #Export avl for manual testing
    session.export_run_files()
    return results
