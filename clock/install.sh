#!/bin/bash

CLOCK_LOCATION=~/.clock_data
LINK_LOC=/usr/local/bin/
LINK_NAME=clock

LINK=$LINK_LOC$LINK_NAME

if [[ ! -e $CLOCK_LOCATION ]]; then
	echo '{}' > $CLOCK_LOCATION
	echo "Creating data file at $CLOCK_LOCATION"
else
	echo "$CLOCK_LOCATION already exists"
fi

if [[ ! -e $LINK ]]; then
	sudo ln -s $PWD/clock.py $LINK
	echo "Creating symbolic link at $LINK"
else
	echo "File already exists at $LINK"
fi
