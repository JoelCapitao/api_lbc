# API LeBonCoin


[![Build Status](https://travis-ci.org/Petlefeu/api_lbc.svg?branch=master)](https://travis-ci.org/Petlefeu/api_lbc)


## Usage
```
usage: api_lbc.py [-h] {dashboard,ad,search} ...

positional arguments:
  {dashboard,ad,search}
                        commands
    dashboard           List dashboard informations
    ad                  Display a particulary ad
    search              Search ads

optional arguments:
  -h, --help            show this help message and exit


# dashboard
usage: api_lbc.py dashboard [-h] [--force-authentication]
                            [--username USERNAME] [--uncolor]

optional arguments:
  -h, --help            show this help message and exit
  --force-authentication, -f
                        To force the authentication.
  --username USERNAME, -u USERNAME
                        Username to log in.
  --uncolor             Disable coloration


# ad
usage: api_lbc.py ad [-h] [--uncolor] key

positional arguments:
  key         ID:CATEGORY of the ad

optional arguments:
  -h, --help  show this help message and exit
  --uncolor   Disable coloration


# search
usage: api_lbc.py search [-h] [--localisation LOCALISATION]
                         [--price-max PRICE_MAX] [--price-min PRICE_MIN]
                         [--uncolor] [--search-in-title] [--sort-by-price]
                         keywords

positional arguments:
  keywords              Keywords of the search

optional arguments:
  -h, --help            show this help message and exit
  --localisation LOCALISATION, -l LOCALISATION
                        Choose a particular localisation
  --price-max PRICE_MAX
                        Set a max price
  --price-min PRICE_MIN
                        Set a in price
  --uncolor             Disable coloration
  --search-in-title     Search keywords only in the ad's title
  --sort-by-price       BETA: Sort list by price
```

## Examples

```bash
# Display your dashboard
python api_lbc.py dashboard


# Display a particular ad
python api_lbc.py ad 1048998842:consoles_jeux_video

# Search an ad
python api_lbc.py search "Vélo VTT"
python api_lbc.py search "Vélo VTT" --localisation paris

# Search more complex
python api_lbc.py search --localisation paris "Vélo VTT" --price-max 500 --price-min 100 --search-in-title
```
