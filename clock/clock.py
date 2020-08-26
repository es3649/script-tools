#!/usr/bin/env python3

# clock.py - a command line time-card system
# Eric Steadman Copyright 2019
#

import copy
import datetime
import json
import os
import sys
import time
import platform
from math import ceil, floor
from os import path

COMMANDS = ('in', 'out', 'help', 'total', 't', 'clear', 'c', 'show', 's', 'list', 'ls', 'rename', 'r')
MESSAGEABLE_COMMANDS = ('in', 'out', 'rename', 'r')
CARD_MAX = 10

if 'Darwin' in platform.platform():
    root = '/Users/'
else:
    root = '/home/'

CLOCK_LOCATION = root + os.getenv('USER') +'/.clock_data'
CLOCK_LOCATION_OLD = root + os.getenv('USER') + '/.clock_data.old'

#################
### Structure ###
#################
# {
#     "1": {
#         "cur": {
#             "in": 1565556903,
#             "out": 1565557532
#         },
#         "punches": [
#             {
#                 "in": 1565496539,
#                 "out": 1565499553
#             },
#             {
#                 "in": 1565556903,
#                 "out": 1565557532
#             }
#         ]
#     },
#     "2": {
#         "cur": {
#             "in": 1565557535
#         },
#         "punches": []
#     }
#     etc...
# }

def parseArgs():
    """
    Parses and verifies command line arguments
    use the help command to see what those arguments should be

    Return:
      (str): the command to execute
      (str): the number of the card to work on, or "0" if not provided
      (str): the message associated with this punch
      (dict): the punch data
    """
    args = sys.argv

    # look for the -m flag and get the message
    msg = 0
    for i, arg in enumerate(args):
        if arg == "-m":
            try:
                msg = args[i+1]
            except:
                raise ValueError(f"Received `-m` flag with no value")
            # slice out the flag and the argument
            args = args[:i] + args[i+2:]
            break

    # ensure argument counts
    if len(args) < 2:
        raise ValueError(f'Expected 1 argument, got {len(args)-1}')
    elif len(args) > 3:
        raise ValueError(f'Expected at most 2 arguments, got {len(args)-1}')

    # ensure valid command
    if args[1] not in COMMANDS:
        raise ValueError(f"Unknown command: '{args[1]}'")

    # get the cards json
    cards = get_card_json()

    # if no card was provided:
    if len(args) < 3:
        return args[1], "0", msg, cards

    # validate the card name
    if len(cards.keys()) >= CARD_MAX and not args[2] in cards.keys():
        raise ValueError("Max number of cards exceeded")

    if args[1] != "in" and not args[2] in cards.keys():
        raise ValueError("Card does not exist")

    # return the card number as a string
    return args[1], args[2], msg, cards

def usage():
    """
    Prints usage data. No args, no return
    """
    print(f'usage: {sys.argv[0]} COMMAND [CARD]')
    print("")
    print("Available commands are:")
    print(" in      punches in on the specified card")
    print(" out     punches out on the specified card")
    print(" show    shows time details for the specified card")
    print(" rename  renames a card, use the message flag to specify new name")
    print(" list    lists the existing cards")
    print(" total   totals the time for the specified card")
    print(" clear   clears punches for the specified card")
    print(" help    displays this message")
    print("")
    print("Available flags are:")
    print(" -m      indicates a message of how the time was spent, or new card name")
    print("")
    print("Specify the card number after any command to run the command on that")
    print(" card. Commands `show`, `total`, and `clear` can be used without a card")
    print(" number, in which case it runs against all cards.")
    print("")
    print(f"The system maintains {CARD_MAX} cards simultaneously")
    print("")
    print("When punching in while already in, punching out while already out")
    print(" or clearing the clock, confirmation is always requested. Then in/out")
    print(" punches will overwrite the previous saved in/out punch")
    print("")
    print(f"Timecard data is saved at {CLOCK_LOCATION}")
    print("")
    print("Created by Eric Steadman, Copyright 2019")
    print("Report bugs to es3649@gmail.com")

def get_card_json():
    """
    Gets the clock object from the data in the clock file

    Return:
      a dictionary representing the deserialized json
    """
    try:
        # check that the file exists
        if not path.exists(CLOCK_LOCATION):
            return dict()
        else:
            with open(CLOCK_LOCATION, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f'Failed to load json with error {str(e)}')
        raise e

def save_card_json(obj):
    """
    Takes an object to serialize and saves it to the clock file

    Arguments:
      obj (obj): the object to serialize and store.
    """
    with open(CLOCK_LOCATION, 'w+') as f:
        json.dump(obj, f, indent="  ")

    
def confirm(prompt, message=""):
    """
    Sends a message then gets a boolean representing a confirmation:
    True if they say yes, False if they say no
    """
    POSITIVE = ('y', 'Y', 'yes', 'Yes', 'YES')
    NEGATIVE = ('n', 'N', 'no', 'No', 'NO')
    while True:
        if message:
            print(message)
        resp = input(prompt + " (y/n) ")
        if resp in POSITIVE:
            return True
        elif resp in NEGATIVE:
            return False
        else:
            print("invalid input")
            print("")

def make_time(epoch_seconds):
    return datetime.datetime.fromtimestamp(epoch_seconds).strftime(r'%Y-%m-%d %H:%M:%S')

def make_time_hms(seconds):
    return f"{seconds//3600}:{seconds%3600//60:02}"

def punch_in(full_card, card_num, msg):
    """
    Punches in with the current time.
    If the last punch was an in punch, then request confirmation,
    then (if affirmative) replace the old in punch with the current time

    Arguments:
      card_number (str): String containing the number of the card to punch in on. Shall be >0
    """
    # get the card from the conglomerate
    if card_num in full_card:
        card = full_card[card_num]
    else:
        # initialize a new card
        card = dict()
        full_card[card_num] = card
        card["cur"] = dict()
        card["punches"] = list()
        print(f"Creating card {card_num}...")

    # grap the current punch
    cur_punch = card["cur"]
    # print(card)

    if "out" in cur_punch or "in" not in cur_punch:
        if "out" in cur_punch:
            # be sure to append a copy, because reference variables
            save = copy.deepcopy(cur_punch)
            card["punches"].append(save)
            del card["cur"]["out"]
            # clear the message if present
            if "msg" in card["cur"]:
                del card["cur"]["msg"]
        now = int(time.time())
        card["cur"]["in"] = now
        # add the message
        if msg != 0:
            card["cur"]["msg"] = msg

        save_card_json(full_card)
        print(f'Punched in at: {make_time(now)}')
    else:
        if not confirm("Overwrite it?", "An 'in' punch already exists."):
            return 
        # else:
        now = int(time.time())
        card["cur"]["in"] = now
        # add the message
        if msg != 0:
            card["cur"]["msg"] = msg
        print(f'Punch overridden, now in at: {make_time(now)}')
        return


def punch_out(full_card, card_num, msg):
    """
    Punches out with the current time.
    If the last punch was an out punch, then request confirmation,
    then (if affirmative) replace the old out punch with the current time

    Arguments:
      full_card (dict): a dictionary containing the timecard data
      card_num (str): String containing the number of the card to punch out on. Shall be >0
    """
    # get the card data
    if card_num in full_card:
        card = full_card[card_num]
    else:
        # initialize a new card
        card = dict()
        full_card[card_num]
        card["cur"] = dict()
        card["punches"] = list()
        print(f"Card number {card_num} is not initialized")
        print("Initializing and not adding an out punch")
        return

    cur_punch = card["cur"]

    if "out" in cur_punch or "in" not in cur_punch:
        # if there is already an out punch
        if "out" in cur_punch:
            if not confirm("Overwrite it?", "An 'out' punch already exists."):
                return 
            # else:
            now = int(time.time())
            card["cur"]["out"] = now
            # add the message
            if msg != 0:
                card["cur"]["msg"] = msg
            save_card_json(full_card)
            print(f'Punch overridden, now out at: {make_time(now)}')

        elif "in" not in cur_punch and len(card["punches"]) == 0:
            # if there are no punches (at all), we can't do anything
            print("Card has no punches (not even an in punch!)")
            print("Not adding an out punch")
            return

    else:
        now = int(time.time())
        card["cur"]["out"] = now
        # add the message
        if msg != 0:
            card["cur"]["msg"] = msg
        save_card_json(full_card)
        print(f'Punched out at {make_time(now)}')


def list_cards(full_card):
    """
    Lists the names of the cards on record
    Now that cards can have names, it will be useful to know which ones there are

    Arguments:
      full_card (dict): a dictionary containing the timecard data
    """
    print("The following cards are available:")
    for key in full_card.keys():
        print(f"  {key}")

def rename(full_card, name, new_name):
    """
    rename will change the name of a card

    Arguments:
      full_card (dict): a dictionary containing the timecard data
      name (str): the name of the card to rename
      new_name (str): the new name of the card
    """
    # be sure not to accidentally overwrite a card
    # this will only move the card if either
    #   1. there was no card with the new name
    #   2. they confirmed the overwrite
    if not new_name in full_card or confirm("Would you like to overwrite it?", f"A card named {new_name} already exists"):
        # if we are overwriting, then overwrite
        if new_name in full_card:
            print("Overwriting...")
        # if just moveing, then move
        else:
            print("Renaming card...")
        # do the move, delete the old card
        full_card[new_name] = full_card[name]
        del full_card[name]
        print(f"Card has been renamed {new_name}")
        save_card_json(full_card)
        return
    # this will only run if they denied an overwrite
    print("Skipping rename...")


def subtotal(full_card, number):
    """
    Totals a single card (0 is invalid input)
    adds up the number of seconds on the record, and returns it

    Arguments:
      full_card (dict): the timecard object to total
      number (int): the number of the card to total

    Return:
      (int): the number of seconds on the card
      (bool): is the clock currently punched in?
    """
    # ensure the card exists
    if number not in full_card:
        print(f"Card {number} does not exist")
        return -1

    # get the card
    card = full_card[number]
    time_sum = 0
    if "in" in card["cur"]:
        punched_in = True


    # add the current punch
    if "out" in card["cur"]:
        time_sum += card["cur"]["out"]-card["cur"]["in"]
        punched_in = False
    else:
        time_sum += int(time.time())-card["cur"]["in"]

    # add each punch we've logged
    for punch in card["punches"]:
        time_sum += punch["out"]-punch["in"]

    return time_sum, punched_in

def total(card_full, name="0"):
    """
    Totals the time on the given card(s) and prints it
    This is a sub function of the show command.

    Arguments:
      card_full (dict): the card json data
      number (str): the number of the card to total, "0" to show all cards
    """
    if name == "0":
        for key in card_full.keys():
            if key in card_full:
                sbt, is_in = subtotal(card_full,key)
                if is_in:
                    msg = " and clocked in"
                else:
                    msg = ""
                print(f"Total card {key}: {make_time_hms(sbt)}{msg}")
    else :
        sbt, is_in = subtotal(card_full,name)
        if sbt != -1:
            if is_in:
                msg = " and is clocked in"
            else:
                msg = ""
            print(f"Card {name} has {make_time_hms(sbt)}{msg}")

def show_one(full_card, card_name):
    """
    Displays the clock data on a single card.

    Arguments:
      full_card (dict): the card json data 
      number (str): the number of the card to show
    """
    before = ceil(21-(len(card_name)-1)/2)
    after = floor(21-(len(card_name)-1)/2)
    for _ in range(before):
        print("=", end="")
    print(f" Card {card_name} ", end="")
    for _ in range(after):
        print("=", end="")
    print("")
    # check existance
    if card_name not in full_card:
        print(f"Card {card_name} does not exist.")
        print(f"--------------------------------------------------")
        return

    card = full_card[card_name]

    for punch in card["punches"]:
        print(f'In: {make_time(punch["in"])}   Out: {make_time(punch["out"])}{" : " + punch["msg"] if "msg" in punch else ""}')
    
    if "out" in card["cur"]:
        print(f'In: {make_time(card["cur"]["in"])}   Out: {make_time(card["cur"]["out"])}{" : " + card["cur"]["msg"] if "msg" in card["cur"] else ""}')
    elif "in" in card["cur"]:
        print(f'In: {make_time(card["cur"]["in"])}   Out: --                 {" : " + card["cur"]["msg"] if "msg" in card["cur"] else ""}')
    
    # print a total for good measure
    print(f"--------------------------------------------------")
    total(full_card, card_name)

def show(full_card, card_name):
    """
    Shows time card data for the given card

    Arguments:
      full_card (dict): the json object holding the card
      card_number (str): String containing the number of the card to show, "0" to show all cards
    """
    if card_name == "0":
        for key in full_card.keys():
            show_one(full_card, key)
            print("")
    
    else:
        show_one(full_card, card_name)
        

def clear(full_card, card_name):
    """
    Requests confirmation, then (if affirmative) clears all clock data from the cards.
    TODO: The data is moved to a '.old' file, whose contents are lost

    Arguments:
      full_card (dict): the json object holding the card
      card_number (str): the number of the card to clear, "0" to clear all cards
    """
    # display the cards for good measure
    show(full_card, card_name)

    if card_name != "0" and card_name not in full_card:
        print("Refusing to delete nonexistant card")
        return

    # get confirmation
    if not (confirm("Delete the selected card(s)?")):
        return

    #else
    if card_name == "0":
        for key in full_card.keys():
            print(f"Deleting card {key}...")
            if key not in full_card:
                print("Refusing to delete nonexistant card")
                continue
            del full_card[key]
    else:
        print(f"Deleting card {card_name}...")
        del full_card[card_name]

    save_card_json(full_card)
    print("Cards have been cleared")

def main():
    cmd, card_num = 0, 0
    try:
        cmd, card_num, msg, card = parseArgs()
        if msg != 0 and not cmd in MESSAGEABLE_COMMANDS:
            raise ValueError(f"Cannot provide message to `{cmd}` command")
    except ValueError as e:
        print(str(e))
        usage()
        return 1
    
    if cmd == 'help':
        usage()
        return 0

    if cmd == 'show' or cmd == 's':
        show(card, card_num)
    elif cmd == 'total' or cmd == 't':
        total(card, card_num)
    elif cmd == 'clear' or cmd == 'c':
        clear(card, card_num)
    elif cmd == 'list' or cmd == 'ls':
        list_cards(card)
    elif cmd == 'rename' or cmd == 'r':
        # in this case, message will be the new name
        rename(card, card_num, msg)

    if card_num == "0":
        card_num = "1"
        
    if cmd == 'in':
        punch_in(card, card_num, msg)
    elif cmd == 'out':
        punch_out(card, card_num, msg)

    return 0

if __name__ == "__main__":
    main()
