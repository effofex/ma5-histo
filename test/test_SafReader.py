import sys, os
import pandas as pd

# update path during runtime to allow test to import local project modules
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

# local project modules
import src.SafReader as sr

# Not the best test in the world, but it does ensure we're up and running
def test_read_saf():
    testDf = pd.read_csv("test\\data\\example_histos.csv")
    safDf  = sr.read("test\\data\\example_histos.saf")
    assert(testDf.equals(safDf))

# TODO almost certainly want to test for graceful errors on malformed *.saf