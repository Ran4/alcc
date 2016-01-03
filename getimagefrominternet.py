import urllib2
import os.path

from os.path import join as opj
import os

def download_image(product_number, verbose=False, overwrite=False):
    """Downloads a certain product number from systembolaget.se
    Returns the path+filename of the saved image, or None on failure
    Example: "product_images\1296.jpg"
    
    If overwrite is True, we will overwrite any now currently existing image.
    """
    image_filename = str(product_number) + ".jpg"
    image_filepath = opj("product_images", image_filename)
    if not overwrite:
        if os.path.exists(image_filepath):
            if verbose:
                print "File %s already exists, won't download!" %\
                    image_filepath
            return image_filepath
    
    url = "http://www.systembolaget.se/" + product_number
    html_data = urllib2.urlopen(url).read()

    for line in html_data.split("\n"):
        
        # ~ print line
        # ~ print
        
        if "_EnlargePicture" in line:
            # print "line:", line
            part_of_url = line.split("<a href=\"")[1].split("\" id=")[0]
            # Eg. /ImageVaultFiles/id_16592/cf_1915/26729.JPG
            image_url = "http://www.systembolaget.se" + part_of_url
            # image_name = part_of_url.split("/")[-1]
            image_data = urllib2.urlopen(image_url).read()
            open(image_filepath, "wb").write(image_data)
            
            if verbose:
                print "Got image for product %s" % product_number
            return image_filepath
    
    if verbose:
        print "Couldn't find image for product number %s" % product_number
    return None

if __name__ == "__main__":
    for product_number in range(1, 250):
        download_image(str(product_number))
