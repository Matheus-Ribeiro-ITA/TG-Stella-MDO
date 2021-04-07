# import logging
#
# # logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
# # logging.warning('This will get logged to a file')
#
# logging.basicConfig(filename='app.log',
#                     filemode='w',
#                     format='%(asctime)s - %(message)s',
#                     datefmt='%d-%b-%y %H:%M:%S')
#
# logging.warning('Admin logged out')

import logging

def createLog():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='myapp.log',
                        filemode='w')
    # logging.basicConfig(level=logging.INFO)
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('../MDO/logging/file.log')
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


logger = createLog()
logger.info("Starting")
logger.warning('This is a warning')
logger.error('This is an error')