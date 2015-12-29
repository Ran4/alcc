"""alccalcer.py
Performs various calculations, and can search systembolaget.se by using it's
API.

alccalcer.py --help shows usage.
"""

import argparse
import sys
import pickle
from operator import itemgetter

import sortimentdownloader
import getimagefrominternet

def getParser():
    """Returns a argparse.ArgumentParser object which is used to parse the
    sysargs
    """
    arg_parser = argparse.ArgumentParser(
        description="AlcCalcer3, a Systembolaget assortment searcher",
        prefix_chars='-/'  #Allow both linux and "windows-style" prefixes
    )
        
    arg_parser.add_argument("searchterms", type=str, nargs='+')
    
    arg_parser.add_argument("-s", "--sort", metavar="TERM",
        help="sort in ascending order according to TERM"
        " (apk/volume/alcohol/price/name)")
        
    arg_parser.add_argument("-d", "--sortd", metavar="TERM",
        help="sort in descending order")
        
    arg_parser.add_argument("-r", "--re", action='store_true',
        help="search using regular expressions")
        
    arg_parser.add_argument("-o", "--out", dest="outfile",
        default="outfile.txt")
    
    arg_parser.add_argument("-p", "--pic", action='store_true',
        help="also downloads and shows images for all matches")
        
    arg_parser.add_argument("-n", type=int,
        help="returns max n results")
        
    arg_parser.add_argument("-m", "--min", nargs=2, metavar=("TERM", "VALUE"),
        help="requires TERM to be equal to or more than VALUE")
        
    arg_parser.add_argument("-M", "--max", nargs=2, metavar=("TERM", "VALUE"),
        help="requires TERM to be equal to or less than VALUE")
    
    return arg_parser
    
class Lookup(object):
    """Class that looks up objects in Systembolaget.
    Will automatically make sure that the sortiment xml file is updated
    by downloading it if needed (not existing/too old)
    """
    def __init__(self):
        self.articles = None
        
    def loadArticles(self):
        """Makes sure that the articles are loaded into memory
        by loading them from a pickled file (which is generated and/or
        downloaded if needed using sortimentdownloader.py)
        """
        update_was_performed = sortimentdownloader.updateIfNeeded(silent=False)
        
        if not self.articles:
            # Didn't just download the article, so we need to load them
            self.articles = pickle.load(open("articles.pickle", "rb"))
            
    def fixTermShortforms(self, term):
        """Takes a string term and changes occurances of e.g. "vol"->"volume"
        """
        term = term.replace("volym", "volume")
        if term == "vol":
            term = "volume"
        
        if "alcohol" not in term:
            term = term.replace("alc", "alcohol")
        term = term.replace("alkohol", "alcohol")
        term = term.replace("abv", "alcohol")
        term = term.replace("pris", "price")
            
        return term
            
    def printMatchDictList(self, args, matchDictList):
        """Takes a list of match dictionaries, sorts them
        if args.sort or args.sortd is set, then prints them to stdout
        """
        SORT_TERMS = ["apk", "volume", "alcohol", "price"]
        if args.sort or args.sortd:
            
            if args.sortd:
                sortTerm = args.sortd
                reverse = True
            else:
                sortTerm = args.sort
                reverse = False
            
            sortTerm = self.fixTermShortforms(sortTerm)
            
            if sortTerm in SORT_TERMS:
                matchDictList.sort(key=itemgetter(sortTerm),
                    reverse=reverse)
            else:
                print("Don't know how to sort by {}".format(args.sort))
            
        numPrinted = 0
        
        for matchDict in matchDictList:
            numPrinted += 1
            
            if args.n is not None and numPrinted > args.n:
                break
                
            print matchDict["matchString"]
            
    def doesSearchtermMatchArticle(self, args, st, article):
        """Returns True if search term string st can be deemed to match
        the article article. Will use regular expressions if args.re is True
        """
        fullArticleName = (article["Namn"] + " " + article["Namn2"]).lower()
        
        if args.re:
            print "Regexp Not implemented yet!"
            return False
        else:
            return st in article["Namn"].lower() or\
                st in fullArticleName or\
                st == article["Artikelid"].lower() or\
                st == article["Varnummer"].lower()
        
    def lookupTermInArticle(self, args, st, article):
        """
        Returns a matchDict of matching
        """
        fullArticleName = (article["Namn"] + " " + article["Namn2"]).lower()
        
        matchDict = None
        if self.doesSearchtermMatchArticle(args, st, article):
            matchString = "%s%s %d cl has apk: %.2f" %\
                (article["Namn"],
                " " + article["Namn2"] if article["Namn2"] else "",
                article["Volymiml"] / 10,
                article["apk"])
                
            matchDict = {
                'matchString': matchString,
                'apk': article["apk"],
                "volume": article["Volymiml"] / 10,
                "alcohol": article["Alkoholhalt"],
                "price": article["Prisinklmoms"],
                "name": fullArticleName,
                "type": article["Varugrupp"],
            }
                
            if args.pic:
                number = article["Varnummer"]
                imageFilePath = getimagefrominternet.downloadImage(number)
                
                if imageFilePath:
                    os.system(imageFilePath)
                    
        if args.max and matchDict:
            term, value = args.max
            
            term = self.fixTermShortforms(term)
            
            if term not in matchDict:
                print "Don't know how to filter by {}".format(term)
                exit()
                
            else:
                if type(matchDict[term]) == float:
                    value = float(value)
                elif type(matchDict[term]) == int:
                    value = int(value)
                    
                if matchDict[term] > value:
                    # print "ignored {} since MAX found".format(matchDict)
                    return None
                    
        if args.min and matchDict:
            term, value = args.min
            
            term = self.fixTermShortforms(term)
            
            if term not in matchDict:
                print "Don't know how to filter by {}".format(term)
                exit()
            else:
                
                if type(matchDict[term]) == float:
                    value = float(value)
                elif type(matchDict[term]) == int:
                    value = int(value)
                
                if matchDict[term] < value:
                    # print "ignored {} since MIN found".format(matchDict)
                    return None
                
        #print "matchDict:", matchDict
                    
        return matchDict
    
    def lookup(self, args):
        self.loadArticles()  #makes sure that the article dict is updated
        
        # print "ready to start lookup!"
        
        matchDictList = []
        for st in args.searchterms:
            for article in self.articles:
                matchDict = self.lookupTermInArticle(args, st, article)
                if matchDict:
                    matchDictList.append(matchDict)
                    
                    # ~ print
                    # ~ print article
                    
                    # ~ print "varugrupp:"
                    # ~ print article["Varugrupp"]
                    # ~ import pdb; pdb.set_trace()
                
        self.printMatchDictList(args, matchDictList)

def main():
    global parser
    parser = getParser()
    
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        # Nothing was given, assume --help
        # argStr = 'bellman pripps'
        # args = parser.parse_args(argStr.split())
        argStr = "--help"
        args = parser.parse_args(argStr.split())
        
    # print args

    lookup = Lookup()
    lookup.lookup(args)

if __name__ == "__main__":
    main()
