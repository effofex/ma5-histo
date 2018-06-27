import pandas as pd
import re

def read(fileLoc):
    """Utility function which parses a MadAnalysis5 *.saf file describing one 
    or more histograms and is capable of translating them to a tidy format for
    further data analysis
    
    Actually read the file and produce a pandas dataframe representing it in
    a Tidy, denormalized table

    Keyword arguments:
    fileLoc -- the path and filename of the *.saf file
    
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

    readState = NONHISTO
    #TODO handle unavailable files
    with open(fileLoc) as fh:
        for l in fh:
            # We could be more elegant, for example do this as a dictionary 
            # mapping of states and parse funcs.  
            #First, let's just bang out a solution
            

            
            # Start in a state where we know we're not within a <Histo> tag
            # usually this means the SAF header or footer
            if(readState == NONHISTO):
                if(re.search('<Histo>', l)):
                    readState=HISTO
                    print("Found histogram")
            # A <Histo> tag can contain <Description>, <Statistics>, or <Data>
            # tags. Without imposing order, detect when those tags crop up or
            # when the <Histo> element closes
            elif(readState == HISTO):
                if(re.search('</Histo>', l)):
                    readState=NONHISTO
                    print("Ended histogram")
                elif(re.search('<Description>', l)):
                    readState=DESC
                    # need to reset the line # of the description
                    # thus the entanglement of a large FSM begins
                    descLine = 0
                    hName = ""      # name of current histogram
                    nbins = 0       # number of bins in current histogram 
                    xmin = 0        # min value in current histogram
                    xmax = 0        # max value in current histogram
                    regions = ""    # region name (this is probaby underspecefiied)

                    print("\tDesc")
                elif(re.search('<Statistics>', l)):
                    readState=STATS
                    
                    # similar element-level state reset as with description
                    statsLine = 0
                    nEvents = 0
                    normEwEvents = 0    # sum of event-weights over events
                    nEntries = 0
                    normEwEntries= 0    # sum of event-weights over entries
                    sumWeightsSq = 0    # sum weights^2
                    sumValWeight = 0    # sum value*weight
                    sumValSqWeight = 0  # sum value^2*weight
                    print("\tStatistics")
                elif(re.search('<Data>', l)):
                    readState=DATA
                    print("\tData")
            # Handle a <Description> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == DESC):
                if(re.search('</Description>', l)):
                    readState=HISTO
                    print("\tEnded Desc")
                else:
                    # description elements contain a few lines, each of which
                    # describe different bits of the histogram. For a rough
                    # implementation, we just keep track of the line # we're
                    # on, and parse accordingly
                    
                    #TODO handle cases where these assumptions don't work
                    if(descLine==0):
                        m=re.search('"(.*)"',l)
                        hName = m.group(1)
                        print("\t\tName: " + hName)
                    elif(descLine==2):
                        nbins,xmin,xmax=l.split()
                        print("\t\tbins: " + nbins)
                        print("\t\tmin: " + xmin)
                        print("\t\tmax: " + xmax)
                    elif(descLine==4):
                        regions = l.split()[0]
                        print("\t\tRegion: " + regions)
                    descLine = descLine + 1
            # Handle a <Statistics> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == STATS):
                if(re.search('</Statistics>', l)):
                    readState=HISTO
                    print("\tEnded Statistics")
                else:
                    # statistics elements are multi-line, handle similar to
                    # description elements
                    
                    # TODO handle cases where these assumptions don't work
                    # TODO find out from @lemouth if we're handling second col 
                    # correctly
                    if(statsLine==0):
                       lhs,rhs = map(int,l.split()[0:2])
                       nEvents = lhs-rhs
                       print("\t\tnEvents: " + str(nEvents))                        
                    elif(statsLine==1):
                       lhs,rhs = map(float,l.split()[0:2])
                       normEwEvents = lhs - rhs
                       print("\t\tnormEwEvents: " + str(normEwEvents))
                    elif(statsLine==2):
                       lhs,rhs = map(int,l.split()[0:2])
                       nEntries = lhs - rhs
                       print("\t\tnEntries: " + str(nEntries)) 
                    elif(statsLine==3):
                       lhs,rhs = map(float,l.split()[0:2])
                       normEwEntries = lhs - rhs
                       print("\t\tnormEwEntries: " + str(normEwEntries))
                    elif(statsLine==4):
                       lhs,rhs = map(float,l.split()[0:2])
                       sumWeightsSq = lhs - rhs
                       print("\t\tsumWeightsSq: " + str(sumWeightsSq)) 
                    elif(statsLine==5):
                       lhs,rhs = map(float,l.split()[0:2])
                       sumValWeight = lhs - rhs
                       print("\t\tsumValWeight: " + str(sumValWeight)) 
                    elif(statsLine==6):
                       lhs,rhs = map(float,l.split()[0:2])
                       sumValSqWeight = lhs - rhs
                       print("\t\tsumValSqWeight: " + str(sumValSqWeight)) 
                    statsLine=statsLine+1
                    
            #TODO retain diagnostic prints as 'verbose' output option?
            # Handle a <Data> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == DATA):
                if(re.search('</Data>', l)):
                    readState=HISTO
                    print("\tEnded Data")
                else:
                    lhs,rhs = map(float,l.split()[0:2])
                    #print(lhs-rhs)
    return pd.DataFrame()


    
