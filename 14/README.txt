The purpose of this assignment was to integrate the signup message from a player
into the printed results and to include the watering hole value when the dealer
sends the start message to the external player.
________________________________________________________________________________

xserver: Starts an Evolution game server listening on port 10001
xclient: Starts an Evolution client running the Silly player strategy.
xgui:    test harness for the display method. Takes a Dealer to display the
         contents of.
xstep:   test harness for the step1 method. Takes a Configuration.
xstep4:  test harness for the step4 method. Takes a list of Action4's.  main:
	 test harness for a full game of Evolution. Takes in a number of players
	 to run the game with.

actions.py: Classes representing the choice of how to use cards.
actions_tests.py: unit tests for the actions classes.
choice.py: Class for representing a dealer -> player choice request.
convert.py: methods to convert between json and python objects
convert_tests.py: unit tests for convert.py methods
dealer.py: the data representation for an Evolution game and the api to
                  progress through it.
dealer_tests.py: unit tests for the dealer object.
display.py: Functions for drawing an Evolution game.
feeding.py: Class representing the feeding choice for a Player.
globals.py: global variables for Evolution
helpers.py: Misc helper functions.
helpers_tests.py: unit test for helper functions.
player.py: the player strategy interface with the next_feeding method.
player_tests.py: unit tests for a Player object
player_state.py: the data representation of the player
player_state_tests: Tests for the PlayerState.
proxy_dealer: Proxy to communicate from the player to the server via TCP.
proxy_player: Proxy to communicate from the dealer to the player via TCP.
species.py: the data representation of a species
species_tests.py: unit tests for a species object
test_utils.py: Test utilities for comparing game objects.
traitcard.py: the data representation of a trait card

tests/xstep/test_xstep.py: python script to test all json file pairs.
tests/xstep4/test_xstep4.py: python script to test all json file pairs.
tests/xsilly/test_xsilly.py: python script to test all json file pairs.

tests/xstep/*:  Test files for xstep.
tests/xstep4/*: Test files for xstep4.
tests/xsilly/*: Test files for xsilly.

________________________________________________________________________________

for  information on starting servers:
./xserver -H

for information on starting clients:
./xclient -H

to run a game of Evolution with n players:
./main n

to run the xsilly test harness with a Choice file called c:
./xsilly < c

to run the test suite, including unit and integration tests:
./test
________________________________________________________________________________

Read the following files (from top to bottom) in order below:

- dealer.py
- dealer_tests.py
- player.py
- player_tests.py
- player_state.py
- player_state_tests.py
- species.py
- species_tests.py
- traitcard.py
- helpers.py
- choice.py
- actions.py
- feeding.py
- display.py

- proxy_player.py
- proxy_dealer.py

- globals.py

- convert.py
- convert_tests.py

- test_utils.py
