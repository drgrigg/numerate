# numerate_python

A command-line utility to find and alter numbers in text files. Designed to be useful for Standard Ebooks producers (standardebooks.org).

Written in Python 3

USAGE:

`numerate [-b --backup] [-f --from ARABIC|ROMAN|TEXT] [-t --to ARABIC|ROMAN|TEXT] [-i --increment] [-d --decrement] DIRECTORY`

example:

`numerate -b -f=ROMAN -t=ARABIC ./samples`

ARABIC|ROMAN|TEXT can be abbreviated, eg:

`numerate -b -f=R -t=A ./samples`
