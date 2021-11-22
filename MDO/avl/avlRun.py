import avl as avl
import os


def avlRun(geometry=None, cases=None):
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

    # Export avl for manual testing
    if 'y' in os.getenv('DEBUG'):
        session.export_run_files()
    return results
