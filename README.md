Performs various calculations, and can search systembolaget.se by using it's
API. Allows queries of Systembolaget's sortiment using a TUI application.

Runs locally: will automatically download the sortiment from Systembolaget when older than 15 days.

## Usage:
`python3 alccalcer.py --help`

```
usage: alccalcer.py [-h] [-s TERM] [-d TERM] [-r] [-o OUTFILE] [-p] [-n N]
                    [-m TERM VALUE] [-M TERM VALUE]
                    searchterms [searchterms ...]

AlcCalcer3, a Systembolaget assortment searcher

positional arguments:
  searchterms

optional arguments:
  -h, --help            show this help message and exit
  -s TERM, --sort TERM  sort in ascending order according to TERM
                        (apk/volume/alcohol/price/name)
  -d TERM, --sortd TERM
                        sort in descending order
  -r, --re              search using regular expressions
  -o OUTFILE, --out OUTFILE
  -p, --pic             also downloads and shows images for all matches
  -n N                  returns max n results
  -m TERM VALUE, --min TERM VALUE
                        requires TERM to be equal to or more than VALUE
  -M TERM VALUE, --max TERM VALUE
                        requires TERM to be equal to or less than VALUE
``` 

## Examples

* Find all products containing the name `riesling` that has a volume of at least 76 cl. Sort according to volume:

```bash
$ python alccalcer.py riesling -m vol 76 -d vol
Wiebelsberg Årgångslåda Riesling Alsace Grand Cru 525 cl
Templárské Ryzlink Rýnský-Riesling 500 cl
Moenchberg Årgångslåda Riesling Alsace Grand Cru 450 cl
Sandahl Riesling Urval 450 cl
Sandahl Riesling Urval 450 cl
```

* Same, but only the first three and also download their images (image downloading is not very reliable), saving output to riesling.txt:

```bash
$ python alccalcer.py riesling -m vol 76 -n 3 -o riesling.txt --pic
```

* Find the 120 cheapest-per-alcohol-amount products that has a volume of max 66 cl:

```bash
$ python alccalcer.py "" -d apk -n 120 -M vol 66 | less
```
