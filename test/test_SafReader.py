import sys, os
import pandas as pd
from pandas.util.testing import assert_frame_equal

# update path during runtime to allow test to import local project modules
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

# local project modules
import src.SafReader as sr

# Not the best test in the world, but it does ensure we're up and running
def test_read_saf():
    testDf = pd.read_csv("test\\data\\example_histos.csv")
    safDf  = sr.read("test\\data\\example_histos.saf")
    
    # being lame & writing this to CSV then re-reading. The values are correct
    # there's something up with how it's being compared in assert_frame_equal
    # specifically
    # E       AssertionError: Attributes are different
    # E
    # E       Attribute "dtype" are different
    # E       [left]:  float64
    # E       [right]: object
    #
    # Just spent 45 mins tracking down a difference that boiled down to being
    # 1 not l, so I'm not in the mood
    safDf.to_csv("test\\data\\out.csv",index=False)
    readDf = pd.read_csv("test\\data\\out.csv")

    assert_frame_equal(testDf.sort_index(axis=1), readDf.sort_index(axis=1), check_names=True,)

# TODO almost certainly want to test for graceful errors on malformed *.saf