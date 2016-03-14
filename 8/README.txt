The purpose of this project was to implement the feed1 method and write a wish
list of the rest of the methods requiired for player -> dealer communication.
________________________________________________________________________________

xstep: test harness for the feed1 method. Takes a JSON Configuration from stdin
       and prints the game's Configuration after a feeding to stdout.

dealer/convert.py: methods to convert between json and python objects
dealer/convert_tests.py: unit tests for convert.py methods
dealer/dealer.py: the data representation for an Evolution game and the api to
                  progress through it.
dealer/dealer_tests.py: unit tests for the dealer object.
dealer/globals.py: global variables for Evolution
dealer/player.py: the player strategy interface with the next_feeding method.
dealer/player_tests.py: unit tests for a Player object
dealer/player_state.py: the data representation of the player
dealer/species.py: the data representation of a species
dealer/species_tests.py: unit tests for a species object
dealer/traitcard.py: the data representation of a trait card

tests/test_all.py: python script to test all json file pairs in the tests dir.
tests/*: json input and output files for integration testing xstep.
________________________________________________________________________________

to run the xstep test harness:
./xstep

to run the test suite, including unit and integration tests:
./test
________________________________________________________________________________

Read the following files (from top to bottom) in order below:
- Streaming/xstep

- traitcard.py
- species.py
- species_tests.py
- player_state.py
- player.py
- player_tests.py
- dealer.py
- dealer_tests.py
- xstep

- convert.py
- convert_tests.py
