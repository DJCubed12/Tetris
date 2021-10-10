import tkinter as tk
from random import choice

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

    def get_ready(self):
        """Show a pop-up window with instructions and a start button."""
        print('TO DO: App.get_ready')


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
        global App

        self.app = App()

        # self.lower_loop = self.Lower_Piece_Thread()
        print('TO DO: Game.Lower_Piece_Thread')
        self.speed = START_SPEED

        self.piece_buffer = self.Piece_Buffer()
        self.hold = None

        # Show instructions and then play
        self.app.get_ready()
        # self.start()

    class Piece_Buffer:
        """Iterator object that generates tetris pieces. Always keeps 5 pieces.

        Instance Variables
        ------------------
        pieces
            A 5 element list describing the coming squence of pieces.
        """

        def __init__(self):
            """Initialize the pieces list and generate the initial pieces."""
            self.pieces = []

            for i in range(5):
                self.gen_new_piece()

        def gen_new_piece(self):
            """Creates a random tetris piece and appends it to the pieces list.

            Uses the global tuple PIECES which contains all tetris piece classes.
            """
            global choice
            global PIECES

            self.pieces.append(choice(PIECES)())

        def __iter__(self):
            """Makes Piece_Buffer an iterator object."""
            return self

        def __next__(self):
            """Pop and return the first piece, append a new piece."""
            piece = self.pieces.pop(0)
            self.gen_new_piece()

            self.update_cvs()

            return piece

        def update_cvs(self):
            """Update the image in the next canvas on the tk application."""
            print('TO DO: Game.Piece_Buffer.update_cvs')


        def __str__(self):
            """Creates a string representation of the coming pieces for debugging."""
            fin = ''
            for piece in self.pieces:
                p = str(piece) + '\n'
                fin += p

            return fin


class Piece:
    """Base class for tetris piece. Can be used as an iterator to get Block objects.

    Instance variables
    ------------------
    orientation : bool list
        A 4 by 4 list of booleans describing the relative positions of all Blocks.
    color : int tuple
        A 3 element list with 0 to 255 range decribing the rbg color to be shown when Blocks are rendered.
    """

    def __init__(self, orientation=None):
        """Initializes the orientation and color variables.

        Parameters
        ----------
        orientation : bool list (default None)
            An optional starting orientation. Used when rotating a piece so that it's new position can be tested before replacing origional orientation. A 4 by 4 list of booleans describing the relative positions of all Blocks.
        """
        if orientation is None:
            self.orientation = [[False for x in range(4)] for y in range(4)]
        else:
            self.orientation = orientation

        self.color = [255, 255, 255]

    def __iter__(self):
        """Creates Block objects representing the current orientation.

        Cycles through the orientation grid and where True, creates a Block object and puts it in a list to iterate.

        Returns
        -------
        Block list
            Returns list of Block objects making up the Piece.
        """
        blocks = []

        for y, row in enumerate(self.orientation):
            for x, tf in enumerate(row):
                if tf:
                    blocks.append(self.Block(self.color, y, x))

        return blocks

    def __str__(self):
        """Creates a string representation of the Piece for debuging."""
        fin = 'Color: ' + str(self.color) + '\n'

        for row in self.orientation:
            fin += str(row) + '\n'

        return fin

    class Block:
        """The individual blocks that make up a tetris piece.

        Primarily used to store the color value of the origional Piece object after it has been placed.

        Instance variables
        ------------------
        color : int tuple
            A 3 element list with 0 to 255 range decribing the rbg color to be shown when rendered.
        offset : int tuple
            A 2 element list describing the Blocks offset from the top left of the Piece's orientation grid. Y offset first, X offset second.
        """

        def __init__(self, color, y_offset, x_offset):
            """Initializes the color and xy_offset variables.

            Parameters
            ----------
            color : int tuple
                A 3 element list with 0 to 255 range decribing the rbg color to be shown when rendered.
            x_offset : int
                The x offset from the top left of the Piece's orientation grid.
            y_offset : int
                The y offset from the top left of the Piece's orientation grid.
            """
            self.color = color
            self.offset = (y_offset, x_offset)

        def __str__(self):
            """Creates a string representation of the Block for debugging."""
            color = 'Color: ' + str(self.color) + '\n'
            offset = '+' + self.offset[0] + ', +' + self.offset[1]

            return color + offset

class I_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False]
        ]

        self.color = [0, 255, 255]
class J_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [False, True, False, False],
        [False, True, False, False],
        [True, True, False, False],
        [False, False, False, False]
        ]

        self.color = [0, 0, 255]
class L_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [True, False, False, False],
        [True, False, False, False],
        [True, True, False, False],
        [False, False, False, False]
        ]

        self.color = [255, 0, 0]
class S_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [False, True, True, False],
        [True, True, False, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = [0, 255, 0]
class Z_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [True, True, False, False],
        [False, True, True, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = [255, 0, 0]
class O_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [True, True, False, False],
        [True, True, False, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = [255, 255, 0]
class T_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [False, True, False, False],
        [True, True, True, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = [128, 0, 128]

PIECES = (I_Piece, J_Piece, L_Piece, S_Piece, Z_Piece, O_Piece, T_Piece)


if __name__ == '__main__':
    game = Game()
    print(game.piece_buffer)
