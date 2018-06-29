import argparse
import SafReader as sr

version = "0.0.1"

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
    
    #print(args)
    #print(args.infile)
    # Parse the file and store as a tidy dataframe
    safDf = sr.read(args.infile)