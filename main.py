import multiprocessing
import os
import sys

if __name__ == "__main__":
    multiprocessing.freeze_support()
    if sys.stdout is None:                 # a windowed build has no console; some libraries print anyway
        sys.stdout = sys.stderr = open(os.devnull, "w")
    from ocr_app.app import main           # use your real package and function names
    main()