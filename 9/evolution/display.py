import Tkinter
from Tkinter import *
import ttk

root = Tk()
root.title("Evolution Dealer")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

ttk.Label(mainframe, text="Game State").grid(column=0, row=0, columnspan=2)
ttk.Label(mainframe, text="Deck:").grid(column=2, row=0)
ttk.Label(mainframe, text="40").grid(column=3, row=0)
ttk.Label(mainframe, text="Watering Hole:").grid(column=4, row=0)
ttk.Label(mainframe, text="10").grid(column=5, row=0)

player = ttk.Frame(mainframe)
player.grid(column=0, row=1, sticky=(N, W, E, S), columnspan=6)
player.columnconfigure(0, weight=1)
player.rowconfigure(0, weight=1)
ttk.Label(player, text="Player1").grid(column=0, row=0, columnspan=2)
ttk.Label(player, text="Hand:").grid(column=2, row=0)
ttk.Label(player, text="[3, burrowing], [5, carnivore]").grid(column=3, row=0)



# feet = StringVar()
# meters = StringVar()
#
# feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
# feet_entry.grid(column=2, row=1, sticky=(W, E))
#
# ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))
# ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)
#
# ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
# ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
# ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)
#
for child in mainframe.winfo_children(): child.grid_configure(padx=10, pady=10)
#
# feet_entry.focus()
# root.bind('<Return>', calculate)

root.mainloop()
