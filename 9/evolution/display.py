import Tkinter
from Tkinter import *
import ttk

def player_display(player_config):
    root = Tk()
    root.title("Evolution Player")

    player = ttk.Frame(root)
    player.grid(column=0, row=0, sticky=(N, W, E, S), columnspan=6)
    player.columnconfigure(0, weight=1)
    player.rowconfigure(0, weight=1)
    ttk.Label(player, text="Player " + str(player_config.name)).grid(column=0, row=0, columnspan=2, sticky=(W))
    ttk.Label(player, text="Hand:").grid(column=2, row=0, sticky=(E))
    ttk.Label(player, text=str(map(lambda tc: str(tc), player_config.hand))).grid(column=3, row=0, sticky=(W))

    for i in range(len(player_config.species)):
        spec = player_config.species[i]
        species0 = ttk.Frame(player)
        species0.grid(column=i, row=1, sticky=(W))
        species0.columnconfigure(0, weight=1)
        species0.rowconfigure(0, weight=1)
        ttk.Label(species0, text="Population:").grid(column=0, row=0, sticky=(E))
        ttk.Label(species0, text="Body:").grid(column=0, row=1, sticky=(E))
        ttk.Label(species0, text="Food:").grid(column=0, row=2, sticky=(E))
        ttk.Label(species0, text="Traits:").grid(column=0, row=3, sticky=(E))
        ttk.Label(species0, text="Fat Food:").grid(column=0, row=4, sticky=(E))
        ttk.Label(species0, text=str(spec.population)).grid(column=1, row=0, sticky=(W))
        ttk.Label(species0, text=str(spec.body)).grid(column=1, row=1, sticky=(W))
        ttk.Label(species0, text=str(spec.food)).grid(column=1, row=2, sticky=(W))
        ttk.Label(species0, text=str(map(lambda tn: tn.encode('utf-8'), spec.trait_names()))).grid(column=1, row=3, sticky=(W))
        ttk.Label(species0, text=str(spec.fat_storage)).grid(column=1, row=4, sticky=(W))

    for child in player.winfo_children(): child.grid_configure(padx=10, pady=10)

    root.mainloop()

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
        player = ttk.Frame(mainframe)
        player.grid(column=0, row=j+1, sticky=(N, W, E, S), columnspan=6)
        player.columnconfigure(0, weight=1)
        player.rowconfigure(0, weight=1)
        ttk.Label(player, text="Player " + str(players[j].name)).grid(column=0, row=0, columnspan=2, sticky=(W))
        ttk.Label(player, text="Hand:").grid(column=2, row=0, sticky=(E))
        ttk.Label(player, text=str(map(lambda tc: str(tc), players[j].hand))).grid(column=3, row=0, sticky=(W))

        for i in range(len(players[j].species)):
            spec = players[j].species[i]
            species0 = ttk.Frame(player)
            species0.grid(column=i, row=1, sticky=(W))
            species0.columnconfigure(0, weight=1)
            species0.rowconfigure(0, weight=1)
            ttk.Label(species0, text="Population:").grid(column=0, row=0, sticky=(E))
            ttk.Label(species0, text="Body:").grid(column=0, row=1, sticky=(E))
            ttk.Label(species0, text="Food:").grid(column=0, row=2, sticky=(E))
            ttk.Label(species0, text="Traits:").grid(column=0, row=3, sticky=(E))
            ttk.Label(species0, text="Fat Food:").grid(column=0, row=4, sticky=(E))
            ttk.Label(species0, text=str(spec.population)).grid(column=1, row=0, sticky=(W))
            ttk.Label(species0, text=str(spec.body)).grid(column=1, row=1, sticky=(W))
            ttk.Label(species0, text=str(spec.food)).grid(column=1, row=2, sticky=(W))
            ttk.Label(species0, text=str(map(lambda tn: tn.encode('utf-8'), spec.trait_names()))).grid(column=1, row=3, sticky=(W))
            ttk.Label(species0, text=str(spec.fat_storage)).grid(column=1, row=4, sticky=(W))

    for child in mainframe.winfo_children(): child.grid_configure(padx=10, pady=10)

    root.after(100, player_display, dealer.player_state(0))
    root.mainloop()
