class SafReader:
    """Utility class which parses a MadAnalysis5 *.saf file describing one or 
    more histograms and is capable of translating them to a tidy format for
    further data analysis
    """
    
    @classmethod
    def read(fileLoc):
    """Actually read the file and produce a pandas dataframe representing it in
    a Tidy, denormalized table

    Keyword arguments:
    fileLoc -- the path and filename of the *.saf file
    
    Returns:
    A pandas dataframe representing all the histogram data
    """