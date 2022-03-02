import os, sys

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api\\app"))

from modelGeneratorControl import ModelControl

if __name__ == "__main__":
    kwargs = {}
    mycontrol = ModelControl()
    try:

        mycontrol.run(**kwargs)

    except:
        mycontrol.endRunOnError()

        raise
