import sys

def progressbar(step,totalSteps, size=60):
    x = int(size*step/totalSteps)
    sys.stdout.flush()
    sys.stdout.write("[%s%s] %i/%i\r" % ("#"*x, "."*(size-x), step, totalSteps))