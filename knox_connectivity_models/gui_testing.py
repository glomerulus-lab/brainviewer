from tkinter import *

#window dimensions
window_dim = "300x400+10+20"

window = Tk()
window.title('Brainviewer')
window.geometry(window_dim)

greeting = Label(text="Welcome to BrainviewerUI!")
greeting.pack()

#on mouse motion within the window, changes the title to reflect coords of mouse pos.

def get_cursor_position(event):
    cursor_coords = '{}, {}'.format(event.x, event.y)
    window.title(cursor_coords)

#on mouse motion within the window, change title to reflect cursor position    
window.bind('<Motion>', get_cursor_position)
window.mainloop()
