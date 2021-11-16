# numerate

A command-line utility to find and alter numbers in text files. Designed to be useful for Standard Ebooks producers (standardebooks.org).

Written in Python 3

USAGE:

`numerate [-b --backup] [-f --from ARABIC|ROMAN|TEXT] [-t --to ARABIC|ROMAN|TEXT] [-i --increment] [-d --decrement] [-p --pattern PATTERN] DIRECTORY`

example:

`numerate -b -f=ROMAN -t=ARABIC -p="CHAPTER {NUMBER}" ./samples`

ARABIC|ROMAN|TEXT can be abbreviated, eg:

`numerate -b -f=R -t=A  -p="CHAPTER {NUMBER}" ./samples`

The token {PATTERN} is used rather than a regular expression as these can be very complex to enter correctly on the command-line and in any case the ARABIC|ROMAN|TEXT choice dictates what regex to use internally. I may add an additional -x command to enter a full regex at a future point.

If the -p option is ommitted, the default is just "{NUMBER}".

For ARABIC, the regular expression used is \d+
For ROMAN, the regular expression used is [IVXLC]+ and the result is checked for validity as a Roman numeral
For TEXT, the regular expression used is [A-Za-z\- ]+ and textual numbers are valid up to NINETY-NINE

