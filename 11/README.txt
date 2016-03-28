The purpose of this project was to implement the player and dealer gui's to
display their current states.
________________________________________________________________________________

xgui: test harness for the display method. Takes a Dealer to display the contents of.

evolution/convert.py: methods to convert between json and python objects
evolution/convert_tests.py: unit tests for convert.py methods
evolution/dealer.py: the data representation for an Evolution game and the api to
                  progress through it.
evolution/dealer_tests.py: unit tests for the dealer object.
evolution/globals.py: global variables for Evolution
evolution/player.py: the player strategy interface with the next_feeding method.
evolution/player_tests.py: unit tests for a Player object
evolution/player_state.py: the data representation of the player
evolution/species.py: the data representation of a species
evolution/species_tests.py: unit tests for a species object
evolution/traitcard.py: the data representation of a trait card

tests/test_all.py: python script to test all json file pairs in the tests dir.
tests/*: json input and output files for integration testing xstep.
________________________________________________________________________________

to run the display test harness:
./xgui

to run the test suite, including unit and integration tests:
./test
________________________________________________________________________________

Read the following files (from top to bottom) in order below:
- xgui
- evolution/display.py

- evolution/traitcard.py
- evolution/species.py
- evolution/species_tests.py
- evolution/player_state.py
- evolution/player.py
- evolution/player_tests.py
- evolution/dealer.py
- evolution/dealer_tests.py

- evolution/convert.py
- evolution/convert_tests.py
