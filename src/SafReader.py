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
    
    NONHISTO    = 1
    HISTO       = 2
    DESC        = 3
    STATS       = 4
    DATA        = 5
    
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
                    print("\tDesc")
                elif(re.search('<Statistics>', l)):
                    readState=STATS
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
                    todo = True    
            # Handle a <Statistics> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == STATS):
                if(re.search('</Statistics>', l)):
                    readState=HISTO
                    print("\tEnded Statistics")
                else:
                    todo = True    
            # Handle a <Data> element. Assumes we  go back to a parent
            # <Histo> element when done.
            elif(readState == DATA):
                if(re.search('</Data>', l)):
                    readState=HISTO
                    print("\tEnded Data")
                else:
                    todo = True                      
                
    return pd.DataFrame()


    
