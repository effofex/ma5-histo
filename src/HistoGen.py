import argparse
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

import SafReader as sr

version = "0.0.1"

# TODO perhaps put this in its own module
# TODO probably provide more control over file writing
def build_histograms(df,writeFiles=False,outdir=".",verbose=False,terse=False):
    """Using a dataframe representing a MadAnalysis5 histogram set as tidy,
    denormalized table build a collection of matplotlib figures representing
    those histograms and optionally write them to disk

    Keyword arguments:
    df -- dataframe containing histogram data
    writeFiles -- save histograms to disk
    outdir -- directory in which files should be written
    verbose --  provide lots of output while working
    terse -- provide minimal output while working
    
    Returns:
    A collection matplotlib figures
    """
    # make life easier by representing relevant columns in df as floats
    floatCols=['binMin', 'binMax', 'value']
    df[floatCols] = df[floatCols].apply(pd.to_numeric, errors='coerce')
    df["bin"]=(safDf.binMin+safDf.binMax)/2
    
    #for now, ignore the over/underflow bins - next version will include
    df = df[df.binMax != np.inf]
    df = df[df.binMin != -1*np.inf]
    df["binlabel"]=(df.binMin+df.binMax)/2
    
    #generate a unique matplotlib figure for each histogram in the df
    
    figno=1
    
    #store the figs for returning and more processing
    figs = []
    # h is a histogram, identified by unique IDs in the df
    for h in df.ID.unique() :
        # these seem like reasonable defaults, they should ideally be
        # user configurable without having to muck about with th returned figs
        f = plt.figure(figno, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
        # since our histo data is already binned, use the weighted version to
        # reproduce it
        plt.hist(df[df.ID==h].binlabel,bins=df[df.ID==h].binMin,weights=df[df.ID==h].value)
        plt.title(df[df.ID==h].name.unique())
        if(writeFiles):
            # TODO handle exceptions on not being able to write
            # Should also be smarter about using os path tools to build path
            plt.savefig(outdir+'\\Fig_'+str(figno)+'.png', bbox_inches='tight')
            if(verbose):
                print("Wrote " + outdir+'\\Fig_'+str(figno)+'.png') 
        figs.append((f,df[df.ID==h]))
        figno=figno+1
    if(terse):
        action = "Wrote " if writeFiles else "Built "
        print(action + str(figno-1)+ " histograms.") 
    return(figs)
    
# Running as a script
if __name__ == "__main__":
    # Handle CLI arguments
    parser = argparse.ArgumentParser(prog="HistoGen", 
    description='Generate some MadAnalysis5 histograms from an associated SAF file.')
    parser.add_argument('infile', type=str, help='Path to a a valid SAF file describing histogram data')
    parser.add_argument('-o','--outdir', type=str, action='store', help='Location in which to store generated histograms ((default is current dir)')
    parser.add_argument('--verbose', action='store_true', help='Provide lots of output during run (default is silent)')
    parser.add_argument('-t','--terse', action='store_true', help='Provide some  output during run (default is silent)')
    parser.add_argument('-v','--version', action='version', version='%(prog)s '+version)
    args = parser.parse_args()
   
    
    # Parse the file and store as a tidy dataframe
    # probably a much better way to handle verbose/terse flags, but this works
    safDf = sr.read(args.infile,args.verbose,args.terse)
    build_histograms(safDf,writeFiles=True,outdir=args.outdir,verbose=args.verbose,terse=args.terse)