"""Is used to handle the download of the sortiment file to disk, parsing it
and finally pickling the results.
"""
import urllib2
import os.path
import time
import pickle

SORTIMENT_XML_FILENAME = "sortiment.xml"
ARTICLES_PICKLE_DUMP_FILENAME = "articles.pickle"

def update_if_needed(silent=True):
    """Will download and save a new sortiment file if needed
    Returns True if update was done, False otherwise
    """
    # Only download if database is older than 15 days
    oldest_file = 15 * 24 * 60 * 60.
    
    current_xml_file_time = os.path.getmtime(SORTIMENT_XML_FILENAME)
    if os.path.exists(SORTIMENT_XML_FILENAME) and\
            time.time() - current_xml_file_time < oldest_file:
        # creation_time = os.path.getctime(SORTIMENT_XML_FILENAME)
            
        if not os.path.exists(ARTICLES_PICKLE_DUMP_FILENAME):
            print "Missing pickled articles file '%s', will parse XML "\
                "and pickle..." % ARTICLES_PICKLE_DUMP_FILENAME
            parse_and_save_articles(silent)
        
        # ~ if not silent:
            # ~ print "The xml file created at %s is new enough" %\
                # ~ time.ctime(creation_time)
        return False

    if not silent:
        print "Redownloading xml file since it's older than %s s (%s days)..."\
            % (oldest_file, oldest_file / 60. / 60. / 24.)
    download_sortiment_file(silent)
    parse_and_save_articles(silent)
        
    return True

def parse_and_save_articles(silent):
    """Loads articles from the xml file with path SORTIMENT_XML_FILENAME,
    then saves them as a pickle dump.
    """
    if not silent:
        print "Parsing xml file..."
    articles = parse_xml_file(silent)
    save_articles_as_pickle_dump(articles, silent)

def save_articles_as_pickle_dump(articles, silent=True):
    """Takes a dict of articles and writes them to a pickled file
    with path ARTICLES_PICKLE_DUMP_FILENAME"""
    pickle.dump(articles, open(ARTICLES_PICKLE_DUMP_FILENAME, "wb"))
    
    if not silent:
        print "Saved articles as a articles.pickle"
    
def parse_xml_file(silent=True):
    """Loads xml file SORTIMENT_XML_FILENAME and parses parts of
    it's XML content. Returns an articles dictionary.
    """
    start_time = time.time()
    
    with open(SORTIMENT_XML_FILENAME) as f:
        raw_xml = f.read()
        
    raw_xml = raw_xml.split("</info>")[1].split("</artiklar>")[0]
    raw_full_article = raw_xml.split("</artikel>")[:-1]
    
    articles = []
    # fullKeyList = "nr,Artikelid,Varnummer,Namn,Namn2,Prisinklmoms,Volymiml,
    # PrisPerLiter,Saljstart,Slutlev,Varugrupp,Forpackning,Forslutning,Ursprung,
    # Ursprunglandnamn,Producent,Leverantor,Argang,Provadargang,Alkoholhalt,
    # Modul,Sortiment,Ekologisk,Koscher".split(",")
    key_list = "Namn,Namn2,Prisinklmoms,Volymiml,Alkoholhalt,Artikelid,"\
        "Varnummer,Varugrupp".split(",")
    for raw_article in raw_full_article[:]:
        raw_article = raw_article.split("<artikel>")[1]
        
        article = {}
        for key in key_list:
            if "<%s>" % key not in raw_article:
                article[key] = ""  #none found
                continue
                
            val = raw_article.split("<%s>" % key)[1].split("</%s>" % key)[0]
            
            if key == "Alkoholhalt":
                # Remove the last percent sign and make to float, eg. "40%"->40
                val = float(val[:-1])
                
            if key == "Prisinklmoms" or key == "Volymiml":
                val = float(val)
            
            article[key] = val
        
        # Calculate and add apk information
        alc = article["Alkoholhalt"]
        volume = article["Volymiml"]
        price = article["Prisinklmoms"]
        article["apk"] = 0.01 * alc * volume / price
        
        articles.append(article)
        
        # ~ for key, val in article.items():
            # ~ print key + ":", val
        # ~ print
    
    if not silent:
        dt = time.time() - start_time
        print "Got %s articles after %.3f s" % (len(articles), dt)
    
    return articles
    
def download_sortiment_file(silent=True):
    """Downloads a xml data file of Systembolaget's sortiment
    using a hard-coded url (dangerous!)
    """
    xml_url = "http://www.systembolaget.se/Assortment.aspx?Format=Xml"
    
    try:
        get = urllib2.urlopen(xml_url)
        xml_data = get.read()
        
        if not silent:
            print "Got xml data from %s" % xml_url
    except:
        print "Error downloading xml file from %s" % xml_url
        exit()
        
    try:
        with open(SORTIMENT_XML_FILENAME, "w") as f:
            f.write(xml_data)
            
        if not silent:
            print "Saved xml data to %s" % SORTIMENT_XML_FILENAME
    except:
        print "Error saving sortiment file"
        exit()
    
if __name__ == "__main__":
    update_if_needed(silent=False)
