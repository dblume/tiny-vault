[![License](https://img.shields.io/badge/license-MIT_license-blue.svg)](https://raw.githubusercontent.com/dblume/tiny-vault/main/LICENSE)
![python3.x](https://img.shields.io/badge/python-3.x-green.svg)
![no AI](https://img.shields.io/badge/no_AI-blue.svg)

## Tiny Vault

A tiny website that attempts to securely store personal data like passwords.
It was written in 2011, in Python 2. Releasing in 2024 in Python 3, but it retains
its web-1.0 spirit.


## How tiny is it?

The heart of the site boils down to just two files.

- index.py
  - Shows a sign-in screen if you haven't signed in yet.
  - Shows a filtered table of your data if you have signed in.
- edit.py
  - Shows an edit form for one of the rows in the table.

No frameworks. Everything else is just support for the above.

![tiny-vault-flow.png](https://raw.githubusercontent.com/dblume/tiny-vault/main/images/tiny-vault-flow.png)


## What makes this vault great?

The most common usecase, getting a password, has a quick and easy flow. Ex.,

1. Enter your master password if you're not already signed in.
2. The filter list is displayed with focus on filter edit box. Type "sof" and
   the filter will interactively hide everything that doesn't match, eventually
   leaving nothing but your "SoFi Bank" entry.
3. Just select the password, and it's auto-copied to your clipboard. (Depending
   on browser support.)

You didn't have to scroll, select edit boxes, move a cursor much, type much or
use shortcut key combos. It's fast and efficient.

## What about the security and encryption?

Tiny Vault relies on running behind TLS (HTTPS). And it relies on you creating
a secure master password for yourself.

It does not store passwords or hashes of passwords. It only stores encrypted
vault files.

![tiny-vault-security.png](https://raw.githubusercontent.com/dblume/tiny-vault/main/images/tiny-vault-security.png)

The above diagrams were made with [Excalidraw](https://excalidraw.com/).


## Getting Started

### Requirements

It was only written to run in Apache. The .htaccess files are important.
If you want to migrate to another server, please specify the same rules on that server.

- Apache
- TLS (Consider [Let's Encrypt](https://letsencrypt.org/) for your certificates.)


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

To create the first account for \<username>:

    ./new_user_and_password.py <username>

The script will ask you for the password you want to associate with that username.


## Is it ready for primetime?

Probably not. Help make it better by being the first to collect the $1337 
vulnerability bounty.


## The $1337 what?

If you find a vulnerability in the code, and it grants you access to the vault
at [tiny-vault](https://tiny-vault.betterfool.com/) even though I didn't give
you credentials, that's possibly worth a bounty to me.

To apply for the bounty, follow the instructions hidden in the vault at
[tiny-vault](https://tiny-vault.betterfool.com/). The fact that I haven't
given you the account (yet) or password (never will) is intentional.

Please don't DDoS the site with brute force attempts. It can't handle it, and
[the site shuts down](https://github.com/dblume/tiny-vault/blob/main/transactionlog.py#L83)
and I don't use master passwords vulnerable to social attacks or lists like
rockyou.txt. I am not the path to the bounty, a vulnerability in the code is.

I won't reward the bounty to vulnerability reports that weren't issued per the
hidden instructions in the vault.

This offer is non-binding and at my sole discretion. If it causes any trouble
it goes away.


## Is it any good?

[Yes](https://news.ycombinator.com/item?id=3067434).


## License

This software uses the [MIT license](https://raw.githubusercontent.com/dblume/tiny-vault/main/LICENSE)
