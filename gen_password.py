#!/usr/bin/env python3
#
# http://www.evanfosmark.com/2009/07/creating-fake-words/

import string
import secrets
from collections import defaultdict
import config

vowels = 'aeiou'

digraphs = ['br', 'ch', 'ck', 'gh', 'ph', 'qu', 'sh', 'st',
            'th', 'wh', 'zh']

consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'p',
              'r', 's', 't', 'v', 'w', 'x', 'y', 'z']

def _vowel():
    return secrets.choice(vowels)


def _consonant():
    return secrets.choice(consonants + digraphs)


def _cv():
    return _consonant() + _vowel()


def _cvc():
    return _cv() + _consonant()


_syllables = [_vowel, _cv, _cvc]

def _syllable():
    return secrets.choice(_syllables)()


def _syllable_of_type(index, last_chars):
    if last_chars in digraphs:
        new_syllable = _syllables[index]()
        while new_syllable[:2] == last_chars:
            new_syllable = _syllables[index]()
        return new_syllable
    else:
        return _syllables[index]()


def password():
    """ Returns a somewhat random password, depending on the algorithm you choose.
    """

    # More secure, but less readable
    alphabet = string.ascii_letters + string.digits + \
               string.punctuation.translate(str.maketrans('', '', '\'"\\`'))
    while config.complex_password_alg:
        password = ''.join(secrets.choice(alphabet) for i in range(12))
        if (any(c.islower() for c in password)
               and any(c.isupper() for c in password)
               and any(c in string.punctuation for c in password)
               and any(c.isdigit() for c in password)):
            return password

    # More readable and "word selectable"
    # Create some random syllables, and join them together into somthing wordish.
    min_length = 5 + secrets.randbelow(3)

    choices = []
    prev_choice = 2
    prev_prev_choice = 2
    for i in range(min_length):
        if prev_prev_choice < 2 and prev_choice == 0:  # if ending with two vowels
            choice = 1 + secrets.randbelow(2)  # exclude starting with a vowel
        else:
            choice = secrets.randbelow(3)
        choices.append(choice)
        prev_prev_choice = prev_choice
        prev_choice = choice

    word = ""
    syllables = []
    while len(word) < min_length:
        syllables.append(_syllable_of_type(choices.pop(0), word[:-2]))
        if syllables[-1].endswith('qu'):
            syllables[-1] += secrets.choice('aeio')
        word += syllables[-1]
    # Capitalize something and stick a number and a '_' in there.
    index = 0  # random.randrange(len(syllables))
    syllables.insert(index, str.capitalize(syllables.pop(index)))

    # Add number and underscore to beginning or end, either  #_... or ..._#
    if secrets.randbelow(2):
        insertion_point = 0
        syllables.insert(insertion_point, '_')
    else:
        insertion_point = len(syllables)
        syllables.insert(insertion_point, '_')
        insertion_point = len(syllables)
    syllables.insert(insertion_point, secrets.choice(string.digits[2:]))
    return "".join(syllables).replace('O', 'A').replace('I', 'Y')


if __name__=='__main__':
    for i in range(10):
        print(password())

