import logging
from datetime import date


def createLog(name=None):
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                     datefmt='%m-%d %H:%M',
    #                     filename=f'logs\\{name}.log',
    #                     filemode='a')
    # logging.basicConfig(level=logging.INFO)
    # Create a custom logger
    logger = logging.getLogger(name)

    # Create handlers
    c_handler = logging.StreamHandler()
    # today = date.today().strftime("%d_%m_%y")
    f_handler = logging.FileHandler(f'logs\\{name}.log')
    c_handler.setLevel(logging.WARNING)
    f_handler.setLevel(logging.INFO)


    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger