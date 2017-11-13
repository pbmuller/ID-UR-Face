import os
try:
	from Tkinter import *
except:
	from tkinter import *

root = Tk()

def hey():
	popup = Tk()
	popup.wm_title("pooop")
	labelBonus = Label(popup, text="its a popup")
	labelBonus.grid(row=0, column=0)

def lock():
	os.popen('gnome-screensaver-command --lock')

toolbar = Frame(root)

b = Button(toolbar, text="popup window", width = 40, command=hey)
b.pack(side = LEFT, padx = 3, pady = 10)

a = Button(toolbar, text="lock", width = 40, command=lock)
a.pack(side = LEFT, padx = 3, pady = 10)

toolbar.pack(side=TOP, fill=X)

mainloop()