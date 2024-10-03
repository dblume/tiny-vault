[![License](https://img.shields.io/badge/license-MIT_license-blue.svg)](https://raw.githubusercontent.com/dblume/tiny-vault/main/LICENSE)
![python3.x](https://img.shields.io/badge/python-3.x-green.svg)

## Tiny Vault

A tiny website that attempts to securely store passwords.

This was written in 2011, in Python 2. Releasing in 2024

## Getting Started

    git clone https://github.com/dblume/tiny-vault.git
    cd tiny-vault
    python3 -m pip install -r requirements.txt
    cp .htaccess.sample .htaccess
    cp data/.htaccess.sample data/.htaccess
    cp config.py.sample config.py
    TODO: Edit config.py
    cp smtp_creds.py.sample smtp_creds.py
    TODO: Edit smtp_creds.py


## TODO

- Type hints
- Add comments
- PEP-8
  -  python3 -m pip install pycodestyle
  -  \#pycodestyle --first --ignore=E501 \*.py
  -  \#pycodestyle --show-source --show-pep8 --ignore=E501 \*.py  \# --show-pep8 implies --first
  -  pycodestyle --first --show-source --ignore=E501 \*.py
- Maybe re-structure

## Is it ready for primetime?

No.


## Is it any good?

[Yes](https://news.ycombinator.com/item?id=3067434).


## License

This software uses the [MIT license](https://raw.githubusercontent.com/dblume/tiny-vault/main/LICENSE)
