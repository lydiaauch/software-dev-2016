import Tkinter
from Tkinter import *
import ttk

def display(dealer):
    """
    Renders a dealer's view of the given Dealer.
    :param dealer: The game to display.
    """
    players = dealer.player_states()
    watering_hole = dealer.watering_hole
    deck = dealer.deck
    root = Tk()
    root.title("Evolution Dealer")

    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    ttk.Label(mainframe, text="Game State").grid(column=0, row=0, columnspan=2)
    ttk.Label(mainframe, text="Deck:").grid(column=2, row=0)
    ttk.Label(mainframe, text=str(len(deck))).grid(column=3, row=0)
    ttk.Label(mainframe, text="Watering Hole:").grid(column=4, row=0)
    ttk.Label(mainframe, text=str(watering_hole)).grid(column=5, row=0)

    for j in range(len(players)):
        draw_player(players[j], j+1, mainframe)
    for child in mainframe.winfo_children(): child.grid_configure(padx=10, pady=10)
    root.after(100, player_display, dealer.player_state(0))
    root.mainloop()

def player_display(player_state):
    """
    Draws the data from player_state onto a Frame.
    :param player_state: A PlayerState object to display.
    """
    root = Tk()
    root.title("Evolution Player")
    player = draw_player(player_state, 0, root)
    for child in player.winfo_children(): child.grid_configure(padx=10, pady=10)
    root.mainloop()

def draw_player(player, row, background):
    """
    Draws the player's data at the row'th row on the background.
    :param player: The PlayerState to display.
    :param row: The index of the row to display at.
    :param background: The Frame to draw the player onto.
    """
    player_frame = ttk.Frame(background)
    player_frame.grid(column=0, row=row, sticky=(N, W, E, S), columnspan=6)
    player_frame.columnconfigure(0, weight=1)
    player_frame.rowconfigure(0, weight=1)
    ttk.Label(player_frame, text="Player " + str(player.name)).grid(column=0, row=0, columnspan=2, sticky=(W))
    ttk.Label(player_frame, text="Hand:").grid(column=2, row=0, sticky=(E))
    ttk.Label(player_frame, text=str(map(lambda tc: str(tc), player.hand))).grid(column=3, row=0, sticky=(W))

    for i in range(len(player.species)):
        spec = player.species[i]
        draw_species(spec, player_frame, i)

    return player_frame

def draw_species(spec, background, col):
    """
    Draws the information about the given Species, spec, on the background Frame,
    background.
    :param spec: The Species information to draw.
    :param background: The background Frame to draw on.
    :param col: The column to display the species in within the background's Frame.
    """
    species = ttk.Frame(background)
    species.grid(column=col, row=1, sticky=(W))
    species.columnconfigure(0, weight=1)
    species.rowconfigure(0, weight=1)
    ttk.Label(species, text="Population:").grid(column=0, row=0, sticky=(E))
    ttk.Label(species, text="Body:").grid(column=0, row=1, sticky=(E))
    ttk.Label(species, text="Food:").grid(column=0, row=2, sticky=(E))
    ttk.Label(species, text="Traits:").grid(column=0, row=3, sticky=(E))
    ttk.Label(species, text="Fat Food:").grid(column=0, row=4, sticky=(E))
    ttk.Label(species, text=str(spec.population)).grid(column=1, row=0, sticky=(W))
    ttk.Label(species, text=str(spec.body)).grid(column=1, row=1, sticky=(W))
    ttk.Label(species, text=str(spec.food)).grid(column=1, row=2, sticky=(W))
    ttk.Label(species, text=str(map(lambda tn: tn.encode('utf-8'), spec.trait_names()))).grid(column=1, row=3, sticky=(W))
    ttk.Label(species, text=str(spec.fat_storage)).grid(column=1, row=4, sticky=(W))
