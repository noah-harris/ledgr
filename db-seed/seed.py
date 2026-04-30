from config import *

def load():

    try:
        import local
        local.run()
    except ImportError:
        logger.debug("local.py not found, skipping local seed.")

load()
