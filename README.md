[![License](https://img.shields.io/badge/license-MIT_license-blue.svg)](https://raw.githubusercontent.com/dblume/tiny-vault/main/LICENSE)
![python3.x](https://img.shields.io/badge/python-3.x-green.svg)

## Tiny Vault

A tiny website that attempts to securely store passwords.

This was written in 2011, in Python 2. Releasing in 2024

## Getting Started

### Get the code:

    git clone https://github.com/dblume/tiny-vault.git
    cd tiny-vault
    python3 -m pip install -r requirements.txt

Move the sample config files to their production locations:

    mv .htaccess.sample .htaccess
    mv data/.htaccess.sample data/.htaccess
    mv config.py.sample config.py

Edit config.py. (Change the salts.)

Not sure you really need to do this, but if you want email when there's trouble:

    mv smtp_creds.py.sample smtp_creds.py

And edit the smtp\_creds.py file.

### Make an account

To create the first account for <username>:

    ./new_user_and_password.py <username>

The script will ask you for the password you want to associate with that username.


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
