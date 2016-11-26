# API LeBonCoin

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
python api_lbc.py search "vélo à roues"
python api_lbc.py search "vélo à roues" --localisation paris
```
