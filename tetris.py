import tkinter as tk

import PIL.Image
import PIL.ImageTk


class App:
    """Controls the tkinter application used as an interface for the game."""

    global tk, PIL

    def __init__(self):
        """Create the tkinter window in which the game is played.

        Returns:
            root -- The tk.Tk object that controls the window
        """

        self.root = tk.Tk()
        self.root.title('Tetris')
        # DEBUG
        self.root['bg'] = 'red'

        self.hold_cvs = tk.Canvas(self.root)
        self.hold_cvs.grid(row=0, column=0, sticky='nesw')
        # DEBUG
        self.hold_cvs['bg'] = 'blue'

        self.game_cvs = tk.Canvas(self.root)
        self.game_cvs.grid(row=0, column=1, rowspan=2, sticky='nesw')
        # SIZE
        self.game_cvs.config(width=350, height=700)
        # DEBUG
        self.game_cvs['bg'] = 'orange'
        # Use numpy images, not PIL
        self.test = PIL.ImageTk.PhotoImage(file=r'statics\test.jpg')
        self.game_cvs.create_image((0,0), image=self.test)
        # Use \/ to delete prev. image before creating a new one
        # self.game_cvs.delete('all')

        self.next_cvs = tk.Canvas(self.root)
        self.next_cvs.grid(row=0, column=2, sticky='nesw')
        # DEBUG
        self.next_cvs['bg'] = 'green'

        self.score_lbl = tk.Label(self.root, text='Score:\n0')
        self.score_lbl.grid(row=1, column=2, sticky='esw')

    def run(self):
        """Starts the main event loop for the tkinter application."""
        self.root.mainloop()

    def stop(self):
        """Stop the tk event loop."""
        self.root.quit()


if __name__ == '__main__':
    app = App()
    app.run()
