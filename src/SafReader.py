from __future__ import print_function
import pandas as pd
import numpy as np
import re
from decimal import Decimal

def read(fileLoc,verbose=False,terse=False):
    """Utility function which parses a MadAnalysis5 *.saf file describing one 
    or more histograms and is capable of translating them to a tidy format for
    further data analysis
    
    Actually read the file and produce a pandas dataframe representing it in
    a Tidy, denormalized table

    Keyword arguments:
    fileLoc -- the path and filename of the *.saf file
    verbose --  provide lots of output during parsing
    terse -- provide minimal output during parsing 
    
    Returns:
    A pandas dataframe representing all the histogram data in a tidy,
    denormalized format
    """
    # *.saf files are XML-ish, but not valid xml.  Also, the way we want to
    # represent them as a csv file will involve some derived values.  It's
    # probably not a good idea to just regex our way through this, but a 
    # builtin XML parser isn't going to do the trick either, so let's try
    # a finite state machine approach first.
    
    # Overall goal is to populate a collection of dictionaries, with keys
    # corresponding to columns in our target pandas dataframe
    NONHISTO    = 1
    HISTO       = 2
    DESC        = 3
    STATS       = 4
    DATA        = 5
    
    # both description and stats have some formatting too
    # to avoid nested state machines, we'll start with just keeping
    # track of line numbers.
    descLine =  0
    statsLine = 0
    
    # data is also line dependent, but very mildly, need to know line # to 
    # determine the bin # and range
    dataLine = 0

    # it's not gauranteed that we'll get a unique descriptor for each histo, so
    # let's track an ID code
    ID = 0
    
    # the list of rows we'll eventually turn into a datframe and the dictionary
    # which represents a row (built as we go through the FSM)
    rows = []
    row = dict()
    readState = NONHISTO
    #TODO handle unavailable files
    with open(fileLoc) as fh:
        if terse:
            print("Reading histogram data: ", end='')
        for l in fh:
            # We could be more elegant, for example do this as a dictionary 
            # mapping of states and parse funcs.  
            #First, let's just bang out a solution
            
            # Start in a state where we know we're not within a <Histo> tag
            # usually this means the SAF header or footer
            if(readState == NONHISTO):
                if(re.search('<Histo>', l)):
                    ID = ID+1
                    row["ID"]=ID
                    readState=HISTO
                    if terse:
                        print('.', end='')
                    elif verbose:
                        print("Found histogram")
            # A <Histo> tag can contain <Description>, <Statistics>, or <Data>
            # tags. Detect when those tags crop up or when the <Histo> element 
            # closes
            elif(readState == HISTO):
                if(re.search('</Histo>', l)):
                    readState=NONHISTO
                    if verbose:
                        print("Ended histogram")
                elif(re.search('<Description>', l)):
                    readState=DESC
                    # need to reset the line # of the description
                    # thus the entanglement of a large FSM begins
                    descLine = 0
                    if verbose:
                        print("\tDesc")
                elif(re.search('<Statistics>', l)):
                    readState=STATS
                    
                    # similar element-level state reset as with description
                    statsLine = 0
                    if verbose:
                        print("\tStatistics")
                elif(re.search('<Data>', l)):
                    readState=DATA
                    dataLine=0
                    if verbose:
                        print("\tData: ", end='')
            # Handle a <Description> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == DESC):
                if(re.search('</Description>', l)):
                    readState=HISTO
                    if verbose:
                        print("\tEnded Desc")
                else:
                    # description elements contain a few lines, each of which
                    # describe different bits of the histogram. For a rough
                    # implementation, we just keep track of the line # we're
                    # on, and parse accordingly
                    
                    #TODO handle cases where these assumptions don't work
                    if(descLine==0):
                        m=re.search('"(.*)"',l)
                        row["name"] = m.group(1)
                        if verbose:
                            print("\t\tName: " + row["name"])
                    elif(descLine==2):
                        row["nbins"],row["xmin"],row["xmax"]=l.split()
                        row["xmin"] = '%.6E' % Decimal(row["xmin"])
                        row["xmax"] = '%.6E' % Decimal(row["xmax"])
                        if verbose:
                            print("\t\tbins: " + row["nbins"])
                            print("\t\tmin: " + row["xmin"])
                            print("\t\tmax: " + row["xmax"])
                    elif(descLine==4):
                        row["region"] = l.split()[0]
                        if verbose:
                            print("\t\tRegion: " + row["region"])
                    descLine = descLine + 1
            # Handle a <Statistics> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == STATS):
                if(re.search('</Statistics>', l)):
                    readState=HISTO
                    if verbose:
                        print("\tEnded Statistics")
                else:
                    # statistics elements are multi-line, handle similar to
                    # description elements
                    
                    # TODO handle cases where these assumptions don't work
                    # TODO find out from @lemouth if we're handling second col 
                    # correctly
                    if(statsLine==0):
                       lhs,rhs = map(int,l.split()[0:2])
                       row["nEvents"] = lhs-rhs
                       if verbose:
                        print("\t\tnEvents: " + str(row["nEvents"]))                        
                    elif(statsLine==1):
                       lhs,rhs = map(float,l.split()[0:2])
                       row["normEwEvents"] = '%.6E' % Decimal((lhs - rhs))
                       if verbose:
                        print("\t\tnormEwEvents: " + str(row["normEwEvents"]))
                    elif(statsLine==2):
                       lhs,rhs = map(int,l.split()[0:2])
                       row["nEntries"] = lhs - rhs
                       if verbose:
                        print("\t\tnEntries: " + str(row["nEntries"])) 
                    elif(statsLine==3):
                       lhs,rhs = map(float,l.split()[0:2])
                       row["normEwEntries"] = '%.6E' % Decimal((lhs - rhs))
                       if verbose:
                        print("\t\tnormEwEntries: " + str(row["normEwEntries"]))
                    elif(statsLine==4):
                       lhs,rhs = map(float,l.split()[0:2])
                       row["sumWeightsSq"] = '%.6E' % Decimal((lhs - rhs))
                       if verbose:
                        print("\t\tsumWeightsSq: " + str(row["sumWeightsSq"])) 
                    elif(statsLine==5):
                       lhs,rhs = map(float,l.split()[0:2])
                       row["sumValWeight"] = '%.6E' % Decimal((lhs - rhs))
                       if verbose:
                        print("\t\tsumValWeight: " + str(row["sumValWeight"])) 
                    elif(statsLine==6):
                       lhs,rhs = map(float,l.split()[0:2])
                       row["sumValSqWeight"] = '%.6E' % Decimal((lhs - rhs))
                       if verbose:
                        print("\t\tsumValSqWeight: " + str(row["sumValSqWeight"] )) 
                    statsLine=statsLine+1
                    
            #TODO retain diagnostic prints as 'verbose' output option?
            # Handle a <Data> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == DATA):
                if(re.search('</Data>', l)):
                    # at the end of the data element, we should have everything
                    # we need to write out a row for the dataframe, so let'saf
                    # store it in a dictionary, then add that to our collection
                    #TODO
                    readState=HISTO
                    if verbose:
                        print("\n\tEnded Data")
                else:
                    lhs,rhs = map(float,l.split()[0:2])
                    binWidth = ((float(row["xmax"])-float(row["xmin"]))/float(row["nbins"]))
                    row["isUnderflow"]=(dataLine==0)
                    row["isOverflow"]=(dataLine>float(row["nbins"]))
                    if(row["isUnderflow"]):
                        binLbInc = -1*np.inf
                        binUbExc = float(row["xmin"])
                        row["isUnderflow"]=True
                    elif(row["isOverflow"]):
                        binLbInc = float(row["xmax"])
                        binUbExc = np.inf
                    else:
                        binLbInc = float(row["xmin"])+binWidth*(dataLine-1)
                        binUbExc = binLbInc+binWidth
                    tol=1e-10
                    if(abs(binLbInc)<tol):
                        binLbInc=0e0
                    if(abs(binUbExc)<tol):
                        binUbExc=0e0
                    row["value"]='%.6E' % Decimal(lhs-rhs)
                    row["binMin"]='%.6E' % Decimal(binLbInc)
                    row["binMax"]='%.6E' % Decimal(binUbExc)
                    if verbose:
                        print(".", end='')
                    rows.append(dict(row))
                    dataLine=dataLine+1
    if terse:
        print('\n', end='')
    df = pd.DataFrame(rows)
    # I don't necessarily care about column order, but making it match up with
    # the test data here is easier than getting the assert to deal with it
    df = df[['ID','name','binMin','binMax','region','value','isUnderflow','isOverflow','nbins','xmin','xmax','nEvents','normEwEvents','nEntries','normEwEntries','sumWeightsSq','sumValWeight','sumValSqWeight']]
    return(df)  
