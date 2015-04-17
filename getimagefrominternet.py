import urllib2, os.path

from os.path import join as opj
import os

def downloadImage(productNumber, verbose=False, overWrite=False):
    """Downloads a certain product number from systembolaget.se
    Returns the path+filename of the saved image, or None on failure
    Example: "product_images\1296.jpg"
    """
    imageFileName = str(productNumber) + ".jpg"
    imageFilePath = opj("product_images", imageFileName)
    if not overWrite:
        if os.path.exists(imageFilePath):
            if verbose:
                print "File %s already exists, won't download!" % imageFilePath
            return imageFilePath
    
    url = "http://www.systembolaget.se/" + productNumber
    htmlData = urllib2.urlopen(url).read()

    for line in htmlData.split("\n"):
        
        #~ print line
        #~ print
        
        if "_EnlargePicture" in line:
            #print "line:", line
            partOfUrl = line.split("<a href=\"")[1].split("\" id=")[0]
            #eg. /ImageVaultFiles/id_16592/cf_1915/26729.JPG
            imageUrl = "http://www.systembolaget.se" + partOfUrl
            imageName = partOfUrl.split("/")[-1]
            imageData = urllib2.urlopen(imageUrl).read()
            open(imageFilePath, "wb").write(imageData)
            
            if verbose:
                print "Got image for product %s" % productNumber
            return imageFilePath
    
    if verbose:
        print "Couldn't find image for product number %s" % productNumber
    return None

if __name__ == "__main__":
    for productNumber in range(1,250):
        downloadImage(str(productNumber))