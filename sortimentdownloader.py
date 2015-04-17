import urllib2, os.path, time, pickle

sortimentXmlFileName = "sortiment.xml"

def updateIfNeeded(silent=True):
    """Will download and save a new sortiment file if needed
    Returns True if update was done, False otherwise
    """
    oldestFile = 15*24*60*60. #Only download if database is older than 15 days
    
    if os.path.exists(sortimentXmlFileName) and\
        time.time() - os.path.getmtime(sortimentXmlFileName) < oldestFile:
        creationTime = os.path.getctime(sortimentXmlFileName)
        
        #~ if not silent:
            #~ print "The xml file created at %s is new enough" %\
                #~ time.ctime(creationTime)
        return False

    if not silent:
        print "Redownloading xml file since it's older than %s s (%s days)..."%\
            (oldestFile, oldestFile/60./60./24.)
    downloadSortimentFile(silent)
    
    if not silent:
        print "Parsing xml file..."
    articles = parseXmlFile(silent)
    
    #dump articles as a pickle
    pickle.dump(articles, open("articles.pickle", "wb"))
    
    if not silent:
        print "Saved articles as a articles.pickle"
        
    return True
    
def parseXmlFile(silent=True):
    startTime = time.time()
    
    with open(sortimentXmlFileName) as f:
        rawXml = f.read()
        
    rawXml = rawXml.split("</info>")[1].split("</artiklar>")[0]
    rawFullArticle = rawXml.split("</artikel>")[:-1]
    
    articles = []
    #fullKeyList = "nr,Artikelid,Varnummer,Namn,Namn2,Prisinklmoms,Volymiml,PrisPerLiter,Saljstart,Slutlev,Varugrupp,Forpackning,Forslutning,Ursprung,Ursprunglandnamn,Producent,Leverantor,Argang,Provadargang,Alkoholhalt,Modul,Sortiment,Ekologisk,Koscher".split(",")
    keyList = "Namn,Namn2,Prisinklmoms,Volymiml,Alkoholhalt,Artikelid,Varnummer,Varugrupp".split(",")
    for rawArticle in rawFullArticle[:]:
        rawArticle = rawArticle.split("<artikel>")[1]
        
        article = {}
        for key in keyList:
            if "<%s>" % key not in rawArticle:
                article[key] = "" #none found
                continue
                
            val = rawArticle.split("<%s>" % key)[1].split("</%s>" % key)[0]
            
            if key == "Alkoholhalt":
                #remove the last percent sign and make to float, eg. "40%" -> 40
                val = float(val[:-1])
                
            if key == "Prisinklmoms" or key == "Volymiml":
                val = float(val)
            
            article[key] = val
        
        #calculate and add apk information
        alc = article["Alkoholhalt"]
        volume = article["Volymiml"]
        price = article["Prisinklmoms"]
        article["apk"] = 0.01 * alc * volume / price
        
        articles.append(article)
        
        #~ for key, val in article.items():
            #~ print key + ":", val
        #~ print
    
    if not silent:
        dt = time.time() - startTime
        print "Got %s articles after %.3f s" % (len(articles), dt)
    
    return articles
    
def downloadSortimentFile(silent=True):
    xmlUrl = "http://www.systembolaget.se/Assortment.aspx?Format=Xml"
    
    try:
        get = urllib2.urlopen(xmlUrl)
        xmlData = get.read()
        
        if not silent:
            print "Got xml data from %s" % xmlUrl
    except:
        print "Error downloading xml file from %s" % xmlUrl
        exit()
        
    try:
        with open(sortimentXmlFileName, "w") as f:
            f.write(xmlData)
            
        if not silent:
            print "Saved xml data to %s" % sortimentXmlFileName
    except:
        print "Error saving sortiment file"
        exit()
    
if __name__ == "__main__":
    updateIfNeeded(silent=False)