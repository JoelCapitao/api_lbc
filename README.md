# API LeBonCoin

[![Build Status](https://travis-ci.org/nbeguier/api_lbc.svg?branch=master)](https://travis-ci.org/nbeguier/api_lbc)

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
usage: api_lbc.py search [-h] [--category CATEGORY] [--location LOCATION]
                         [--price-max PRICE_MAX] [--price-min PRICE_MIN]
                         [--property-type PROPERTY_TYPE] [--region REGION]
                         [--rent-max RENT_MAX] [--rent-min RENT_MIN]
                         [--room-max ROOM_MAX] [--room-min ROOM_MIN]
                         [--search-in-title] [--sort-by-price]
                         [--surface-max SURFACE_MAX]
                         [--surface-min SURFACE_MIN] [--uncolor]
                         keywords

positional arguments:
  keywords              Keywords of the search

optional arguments:
  -h, --help            show this help message and exit
  --category CATEGORY, -c CATEGORY
                        Set the category of the search
  --location LOCATION, -l LOCATION
                        Choose a particular location
  --price-max PRICE_MAX
                        Set a max price
  --price-min PRICE_MIN
                        Set a in price
  --property-type PROPERTY_TYPE
                        Set the property type
  --region REGION       Set the region
  --rent-max RENT_MAX   Set the maximum rent price
  --rent-min RENT_MIN   Set the minimum rent price
  --room-max ROOM_MAX   Set the maximum number of rooms
  --room-min ROOM_MIN   Set the minimum number of rooms
  --search-in-title     Search keywords only in the ad's title
  --sort-by-price       BETA: Sort list by price
  --surface-max SURFACE_MAX
                        Set a max surface
  --surface-min SURFACE_MIN
                        Set a min surface
  --uncolor             Disable coloration
```

## Examples

```bash
# Display your dashboard
python api_lbc.py dashboard


# Display a particular ad
python api_lbc.py ad 1048998842:consoles_jeux_video

# Search an ad
python api_lbc.py search "Vélo VTT"
python api_lbc.py search "Vélo VTT" --location paris


# Search more complex
python api_lbc.py search --location paris "Vélo VTT" --price-max 500 --price-min 100 --search-in-title
python api_lbc.py search "studio" --category locations --location Paris --property-type=appartement --rent-min=500 --rent-max=700 --sort-by-price
python api_lbc.py search "studio" --category ventes_immobilieres --location Paris --property-type=appartement --price-min=150000 --price-max=300000 --room-min=3 --room-max=4
```
