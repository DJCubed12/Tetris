import tkinter as tk

import PIL.Image
import PIL.ImageTk

# CONSTANTS
GAME_SIZE = (350, 700)
START_SPEED = 1500    # milliseconds
SPEED_STEP = 250


class App:
    """Controls the tkinter application used as an interface for the game."""
    global tk, PIL
    global GAME_SIZE

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
        self.game_cvs.config(width=GAME_SIZE[0], height=GAME_SIZE[1])
        # DEBUG
        self.game_cvs['bg'] = 'orange'

        self._game_im = PIL.ImageTk.PhotoImage(file=r'statics\test.jpg')
        self.game_cvs.create_image((0,0), image=self._game_im)
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

    def update_game(self, new_image):
        """Update the image in the game canvas.

        Clear self.game_cvs. Convert PIL Image to PIL ImageTk and place on game_cvs.

        Parameters
        ----------
        new_image : PIL.Image
            A PIL Image object
        """
        self.game_cvs.delete('all')

        self._game_im = PIL.ImageTk.PhotoImage(new_image)
        self.game_cvs.create_image((0,0), image=self._game_im)
    def update_next(self, new_image):
        """Update the image in the next canvas.

        Clear self.next_cvs. Convert PIL Image to PIL ImageTk and place on next_cvs.

        Parameters
        ----------
        new_image : PIL.Image
            A PIL Image object
        """
        self.next_cvs.delete('all')

        self._next_im = PIL.ImageTk.PhotoImage(new_image)
        self.next_cvs.create_image((0,0), image=self._next_im)
    def update_hold(self, new_image):
        """Update the image in the hold canvas.

        Clear self.hold_cvs. Convert PIL Image to PIL ImageTk and place on hold_cvs.

        Parameters
        ----------
        new_image : PIL.Image
            A PIL Image object
        """
        self.hold_cvs.delete('all')

        self._hold_im = PIL.ImageTk.PhotoImage(new_image)
        self.hold_cvs.create_image((0,0), image=self._hold_im)


class Game:
    """The main object of the program. Keeps track of a 10x20 grid where the game is played. Contains functions for rendering, piece movement, and coordincate checking. Hosts the App object."""

    def __init__(self):
        """Creates the App object. Initializes variables."""
        global START_SPEED

        self.app = App()

        # self.lower_loop = self.Lower_Piece_Thread()
        # self.piece_buffer = self.Piece_Buffer()
        print('TO DO: Game.Lower_Piece_Thread')
        print('TO DO: Game.Piece_Buffer')

        self.speed = START_SPEED
        self.hold = None


if __name__ == '__main__':
    Game()
