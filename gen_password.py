#!/usr/bin/python
#!C:/Python26/python.exe
#
# http://www.evanfosmark.com/2009/07/creating-fake-words/

import random
import string
from collections import defaultdict

vowels = ['a', 'e', 'i', 'o', 'u' ]

digraphs = ['br', 'ch', 'ck', 'gh', 'kl', 'ph', 'qu', 'sh', 'st',
            'th', 'wh', 'zh']

consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'p',
              'r', 's', 't', 'v', 'w', 'x', 'y', 'z']

def _vowel():
    return random.choice(vowels)


def _consonant():
    return random.choice(consonants + digraphs)


def _cv():
    return _consonant() + _vowel()


def _cvc():
    return _cv() + _consonant()


_syllables = [_vowel, _cv, _cvc]

def _syllable():
    return random.choice(_syllables)()


def _syllable_of_type(index, last_chars):
    if last_chars in digraphs:
        new_syllable = _syllables[index]()
        while new_syllable[:2] == last_chars:
            new_syllable = _syllables[index]()
        return new_syllable
    else:
        return _syllables[index]()


def password():
    """ This function generates a fake word by creating a few
        random syllables and then joining them together.
    """
    min_length = 5  # random.randint(7, 9)

    choices = []
    prev_choice = 2
    prev_prev_choice = 2
    for i in range(min_length):
        if prev_prev_choice < 2 and prev_choice == 0:
            choice = random.randrange(1, 3)
        else:
            choice = random.randrange(3)
        choices.append(choice)
        prev_prev_choice = prev_choice
        prev_choice = choice

    word = ""
    syllables = []
    while len(word) < min_length:
        syllables.append(_syllable_of_type(choices.pop(0), word[:-2]))
        if syllables[-1].endswith('qu'):
            syllables[-1] += random.choice('aeio')
        word += syllables[-1]
    # Capitalize something and stick a number and a '_' in there.
    index = random.randrange(len(syllables))
    syllables.insert(index, string.capitalize(syllables.pop(index)))
    insertion_point = random.randrange(len(syllables) + 1)
    syllables.insert(insertion_point, random.choice(string.digits[2:]))
    insertion_point = random.randrange(len(syllables) + 1)
    syllables.insert(insertion_point, '_')
    return "".join(syllables)


if __name__=='__main__':
#    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    for i in xrange(5):
        print password()
    print "Done."

