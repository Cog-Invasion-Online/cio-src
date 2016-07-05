########################################
# Filename: GameDeveloperConsole.py
# Created by: blach (27Sep14)
# (CI 2.0.0 - (07Jun14), CIO - (27Sep14))
########################################

import Tkinter

def excecuteCode():
	global app_textbox
	exec (app_textbox.get(1.0, "end"), globals())
	
app = Tkinter.Tk()
app.title("Cog Invasion Developer Console")
app.geometry("440x280")
app.resizable(False, False)

app_frame = Tkinter.Frame(app)

global app_textbox
app_textbox = Tkinter.Text(app_frame, width=70, height=20)
app_textbox.insert(1.0, "")
app_textbox.pack(side="left")

app_submit_button = Tkinter.Button(app, text="Submit", command=excecuteCode)
app_submit_button.pack()
scroll = Tkinter.Scrollbar(app_frame)
scroll.pack(fill="y",side="right")
scroll.config(command=app_textbox.yview)
app_textbox.config(yscrollcommand=scroll.set)
app_frame.pack(fill="y")
app.mainloop()

