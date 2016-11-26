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
```

## Examples

```bash
# Display your dashboard
python api_lbc.py dashboard


# Display a particular ad
python api_lbc.py ad 1048998842 consoles_jeux_video

# Search an ad
python api_lbc.py search "Vélo VTT"
python api_lbc.py search "Vélo VTT" --localisation paris

# Search more complex
python api_lbc.py search --localisation paris "Vélo VTT" --price-max 500 --price-min 100 --search-in-title
```
