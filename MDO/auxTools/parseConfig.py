from configparser import ConfigParser
import os


def parseConfig(pathToFile="outputsConfig.cfg"):
    """
    # Description:
        Read cfg file and pass to environment variables

    ## Parameters:
        - pathToFile[str]:
    ## Returns:
        None
    """
    config = ConfigParser()
    config.read(os.path.join(pathToFile))

    os.environ['DEBUG'] = config['env']['DEBUG']
    os.environ['PLOT'] = config['env']['PLOT']
    os.environ['PRINT'] = config['env']['PRINT']
    os.environ['WEIGHT'] = config['methods']['WEIGHT']
