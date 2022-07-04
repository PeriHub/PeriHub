import logging
from fa_pyutils.service.logger import MyLogger

class MyGlobals(object):
    """This class holds global variables"""

    # ===========================================================================
    # --- general ---
    # ===========================================================================
    progName = "SMETANA"
    runName = "smetana"
    """used as output file names, name of the actual run"""
    description = "SMETANA - Structure Mechanical Evaluation of Automated maNufactured composite pArts."

    major = 17
    minor = 1
    revision = 0  # starting with zero
    """
     care should be taken before changing any version variable (i.e.  Major, minor 
     or Revision variable). 
    """
    version = f"{major}.{minor}.{revision}"

    development = True
    _logLevel = logging.INFO
    """log level as defined in module loghandling. It is a projection of a variable in
    the loghandling module to an integer value. So both may be used.
    - loghandling.NOTSET: 0
    - loghandling.DEBUG: 10
    - loghandling.INFO: 20
    - loghandling.WARNING: 30
    - loghandling.WARN: 30
    - loghandling.ERROR: 40
    - loghandling.CRITICAL: 50
    
    There is one more log level called TIME. In contrast to the others listed here
    TIME is changeable. Please have a look at smetana.service.common.utilities.duration for further information.
    """
    errorLogFileName = "err.log"
    """Name of error log file. it is just used in case of exceptions for storing the traceback."""

    logFileName = "run.log"
    """Name of log file. """

    debugLogFileName = "debug.log"
    """Name of debug log file. Here everything logged is logged to this file for debug purposes."""

    exceptionhookObj = None
    """Object that handles exceptions if not MYGLOBAL.development. It is usually set in main.env"""

    smetana_enabled = False

MYGLOBAL = MyGlobals()

log = MyLogger("logger")

MYGLOBAL.logLevel = log.handlers[0].level
