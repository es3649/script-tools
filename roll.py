#!/usr/bin/env python3

help_str = """
roll is a tool for computing die rolls

Pass any number of arguments of the form
<number>d<number>

The first number refers to the number of dice to roll;
The second refers to the number of sides on the die.
For example, to roll 5, 6-sided dice, pass '5d6'.

It also computes rolls with advantage or disadvantage:
each of these rolls 2 dice instead of one, then chooses
the greater for advantage and the lesser for disadvantage.
Use this option by adding the letter 'a' for advantage 
or the letter 'd' for disadvantage to the end of the 
argument. For example, passing 4d20d will roll 4 pairs
of 20-sided dice, and for each pair will return the lesser
of the two numbers rolled.

Eric Steadman - 2020
"""

import re
import sys
import random
from math import floor

def roll_x_y_sided_dice(x,y):
    """Rolls x, y-sided dice

    Parameters:
        x (int): the number of dice to roll
        y (int): the number of sides on each die
    
    Returns:
        rolls (list): the value of each roll
    """
    return [floor(random.random()*y)+1 for _ in range(x)]

def do_rolls(rolls):
    """accepts a list of 3 tuples, where the first is the number of dice
    to roll, the second is the number of sides on the die, and the third
    is either None, 'a' signifying advantage, or 'd' signifying
    disadvantage

    Parameters:
        rolls (list): the list of rolls to do

    Returns:
        results (list): a list of 2 tuples containing the numbers rolled
            and the total
        total (int): the total for all the rolls
    """
    # result variables
    results = []
    total = 0
    # for each roll we need to do
    for roll in rolls:
        # if it's advantace, handle that
        if roll[2] == 'a':
            # take the max of 2 y-sided dice x times
            result = [max(roll_x_y_sided_dice(2,int(roll[1]))) for _ in range(int(roll[0]))]
        elif roll[2] == 'd':
            # take the min of 2 y-sided dice x times
            result = [min(roll_x_y_sided_dice(2,int(roll[1]))) for _ in range(int(roll[0]))]
        else:
            # take x, y-sided dice
            result = roll_x_y_sided_dice(int(roll[0]), int(roll[1]))
        
        # total them up, add to the running total and the results
        s = sum(result)
        total += s
        results.append((result,s))
    # return the generated rolls
    return results, total

# if this is the main method
if __name__ == "__main__":

    # check for a help message and print it
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'help'):
        print(help_str)
        sys.exit(0)

    # compile a pattern to match the die roll args
    pattern = re.compile(r'^([1-9][0-9]*)d([1-9][0-9]*)(a|d)?$')

    # a list of compiled matches
    matches = []

    # match each roll and get the groups
    for arg in sys.argv[1:]:
        match = pattern.match(arg)
        # bad arg, complain
        if not match:
            print(f"Bad argument: {arg}")
            print(help_str)
            sys.exit(1)
        matches.append(match.groups())

    # do the hard work
    results, grand_total = do_rolls(matches)

    # print results
    for roll, (res, total) in zip(sys.argv[1:], results):
        print(f"{roll:<7}: {total}")
        print(res)
        if len(sys.argv) > 2:
            print()
    
    # print grand total
    if len(sys.argv) > 2:
        print(f"Total: {grand_total}")
