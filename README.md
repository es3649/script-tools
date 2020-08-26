# script-tools

A collection of tools each written as one-file scripts.

## Clock

`clock` is a punchcard script included at `clock/clock.py`.

```
usage: clock COMMAND [CARD]

Available commands are:
 in      punches in on the specified card
 out     punches out on the specified card
 show    shows time details for the specified card
 rename  renames a card, use the message flag to specify new name
 list    lists the existing cards
 total   totals the time for the specified card
 clear   clears punches for the specified card
 help    displays this message

Available flags are:
 -m      indicates a message of how the time was spent, or new card name

Specify the card number after any command to run the command on that
 card. Commands `show`, `total`, and `clear` can be used without a card
 number, in which case it runs against all cards.

The system maintains 10 cards simultaneously

When punching in while already in, punching out while already out
 or clearing the clock, confirmation is always requested. Then in/out
 punches will overwrite the previous saved in/out punch

Timecard data is saved at `/Users/$USER/.clock_data` on MacOS
Timecard data is saved at `/home/$USER/.clock_data` on Linux

Created by Eric Steadman, Copyright 2019
```

## Graph deps

`graph_deps` creates a dependency graph for a project, included at
`graph_deps.py` It supports python and c++ projects so far.

Dependency graphs will be generated as a Graphviz file in the directory
where the script was run. The file can then be translated into an image
using any of the Graphviz compilers. For example:

`$ dot dependencies.gv -Tpng dependencies.png`

```
usage: graph_deps [-h] [-l LANG] [root]

graph_deps analyzes a project and builds the dependency graph of the project
by language

positional arguments:
  root                  the root of the directory to analyze

optional arguments:
  -h, --help            show this help message and exit
  -l LANG, --lang LANG  the language of the project to analyze
```

## Roll

`roll` is a command line script for rolling dice, included at
`roll.py`.

```
roll is a tool for computing die rolls

Pass any number of arguments of the form
<number>d<number>

The first number refers to the number of dice to roll;
The second refers to the number of sides on the die.
For example, to roll 5, 6-sided dice, pass '5d6'.

It also computes rolls with "advantage" or "disadvantage":
each of these rolls 2 dice instead of one, then chooses
the greater for advantage and the lesser for disadvantage.
Use this option by adding the letter 'a' for advantage 
or the letter 'd' for disadvantage to the end of the 
argument. For example, passing 4d20d will roll 4 pairs
of 20-sided dice, and for each pair will return the lesser
of the two numbers rolled.

Eric Steadman - 2020
```
