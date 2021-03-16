import avl.avlwrapper as avl


def avlRun(geometry, cases, DEBUG=False):
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
    # ---------------------------------------------------------------------------------------------------------
    # # Exporting geometry files
    session.export_run_files()
    results = session.run_all_cases()

    #Export avl for manual testing
    if DEBUG:
        session.export_run_files()
    return results
