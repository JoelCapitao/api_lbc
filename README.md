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

## Changelog
- 2.2.0:
  * Add filters feature to search
- 2.1.0:
  * Add feature to disable coloration
  * Bug fix : Address not encoded in utf-8
- 2.0.1:
  * Fix price issue
- 2.0.0:
  * New version of the script.
  * argument rethink
  * function search, ad and dashboard separate
  * fix issue of no price
- 1.9.0:
  * Search function unstable
- 1.8.1:
  * Update README
- 1.8.0:
  * Add : Select a particular ad
- 1.7.3:
  * Add colors
  * Change variables
- 1.7.2:
  * Add a real argparse
- 1.7.1:
  * Replacement of bash script in python
  * Cleaning
  * Display informations in shell
  * Pylint : "Your code has been rated at 10.00/10"
- 1.7.0:
  * New version of the core
  * Maybe unstable...
- 1.6.1:
  * Bug Fix
- 1.6.0:
  * Creation d'un fichier par element
  * Finnissions du code
  * Recuperation de l'URL
- 1.5.1:
  * Changement du help
  * Ajout d'une exception
- 1.5.0:
  * Changement de l'ordre d'apparition
  * Bug fixes
- 1.4.1:
  * Correction du print
- 1.4.0:
  * Changement de l'output
  * Sortie en fichier
  * Entrées différentes
- 1.3.2:
  * Modification du chemin du cookie
- 1.3.1:
  * Ajout de sécurité
  * proprification du code
- 1.2.0:
  * Bug fix
- 1.1.0:
  * maj du code
- 1.0.0:
  * Version stable
