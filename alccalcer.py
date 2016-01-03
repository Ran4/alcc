"""alccalcer.py
Performs various calculations, and can search systembolaget.se by using it's
API.

alccalcer.py --help shows usage.
"""

import argparse
import sys
import pickle
import os
from operator import itemgetter

import sortimentdownloader
import getimagefrominternet


def get_parser():
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
        
    def load_articles(self):
        """Makes sure that the articles are loaded into memory
        by loading them from a pickled file (which is generated and/or
        downloaded if needed using sortimentdownloader.py)
        """
        update_was_performed = \
            sortimentdownloader.update_if_needed(silent=False)
        
        if not self.articles:
            # Didn't just download the article, so we need to load them
            self.articles = pickle.load(open("articles.pickle", "rb"))
            
    def fix_term_shortforms(self, term):
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
            
    def print_match_dict_list(self, args, match_dict_list):
        """Takes a list of match dictionaries, sorts them
        if args.sort or args.sortd is set, then prints them to stdout
        """
        SORT_TERMS = ["apk", "volume", "alcohol", "price"]
        if args.sort or args.sortd:
            
            if args.sortd:
                sort_term = args.sortd
                reverse = True
            else:
                sort_term = args.sort
                reverse = False
            
            sort_term = self.fix_term_shortforms(sort_term)
            
            if sort_term in SORT_TERMS:
                match_dict_list.sort(key=itemgetter(sort_term),
                    reverse=reverse)
            else:
                print "Don't know how to sort by {}".format(args.sort)
            
        num_printed = 0
        
        for match_dict in match_dict_list:
            num_printed += 1
            
            if args.n is not None and num_printed > args.n:
                break
                
            print match_dict["match_str"]
            
    def does_searchterm_match_article(self, args, search_string, article):
        """Returns True if search term string search_string can be deemed to
        match the article article.
        Will use regular expressions if args.re is True
        """
        full_article_name = (article["Namn"] + " " + article["Namn2"]).lower()
        
        if args.re:
            print "Regexp Not implemented yet!"
            return False
        else:
            return search_string in article["Namn"].lower() or\
                search_string in full_article_name or\
                search_string == article["Artikelid"].lower() or\
                search_string == article["Varnummer"].lower()
        
    def lookup_term_in_article(self, args, search_string, article):
        """
        Returns a match_dict of matching
        """
        full_article_name = (article["Namn"] + " " + article["Namn2"]).lower()
        
        match_dict = None
        if self.does_searchterm_match_article(args, search_string, article):
            match_str = "%s%s %d cl has apk: %.2f" %\
                (article["Namn"],
                " " + article["Namn2"] if article["Namn2"] else "",
                article["Volymiml"] / 10,
                article["apk"])
                
            match_dict = {
                'match_str': match_str,
                'apk': article["apk"],
                "volume": article["Volymiml"] / 10,
                "alcohol": article["Alkoholhalt"],
                "price": article["Prisinklmoms"],
                "name": full_article_name,
                "type": article["Varugrupp"],
            }
                
            if args.pic:
                number = article["Varnummer"]
                image_filepath = getimagefrominternet.download_image(number)
                
                if image_filepath:
                    # Open the image using os.system: not optimal
                    os.system(image_filepath)
                    
        if args.max and match_dict:
            term, value = args.max
            
            term = self.fix_term_shortforms(term)
            
            if term not in match_dict:
                print "Don't know how to filter by {}".format(term)
                exit()
                
            else:
                if type(match_dict[term]) == float:
                    value = float(value)
                elif type(match_dict[term]) == int:
                    value = int(value)
                    
                if match_dict[term] > value:
                    # print "ignored {} since MAX found".format(match_dict)
                    return None
                    
        if args.min and match_dict:
            term, value = args.min
            
            term = self.fix_term_shortforms(term)
            
            if term not in match_dict:
                print "Don't know how to filter by {}".format(term)
                exit()
            else:
                
                if type(match_dict[term]) == float:
                    value = float(value)
                elif type(match_dict[term]) == int:
                    value = int(value)
                
                if match_dict[term] < value:
                    # print "ignored {} since MIN found".format(match_dict)
                    return None
                
        # print "match_dict:", match_dict
                    
        return match_dict
    
    def lookup(self, args):
        """Given an argument list args, performs a lookup of articles.
        The articles are automatically loaded (and updated if needed) from
        the internet.
        """
        self.load_articles()  #makes sure that the article dict is updated
        
        # print "ready to start lookup!"
        
        match_dict_list = []
        for search_string in args.searchterms:
            for article in self.articles:
                match_dict = self.lookup_term_in_article(args,
                     search_string, article)
                if match_dict:
                    match_dict_list.append(match_dict)
                    
                    # ~ print
                    # ~ print article
                    
                    # ~ print "varugrupp:"
                    # ~ print article["Varugrupp"]
                    # ~ import pdb; pdb.set_trace()
                
        self.print_match_dict_list(args, match_dict_list)

def main():
    global parser
    parser = get_parser()
    
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        # Nothing was given, assume --help
        # arg_str = 'bellman pripps'
        # args = parser.parse_args(arg_str.split())
        arg_str = "--help"
        args = parser.parse_args(arg_str.split())
        
    # print args

    lookup = Lookup()
    lookup.lookup(args)

if __name__ == "__main__":
    main()
