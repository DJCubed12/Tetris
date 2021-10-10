import tkinter as tk
from random import choice

# DPI Awareness
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

import PIL.Image
import PIL.ImageTk


# CONSTANTS
class Constants:
    """Enum of global constants. (Not actually an enum because it conflicts with PIL)"""
    # MANUALLY ADJUST
    # In milliseconds:
    START_SPEED = 1500
    SPEED_STEP = 250

    # In pixels:
    # Should be divisible by 10
    GAME_WIDTH = 400


    # DON'T MANUALLY ADJUST
    if GAME_WIDTH % 10:
        raise ValueError('_GAME_WIDTH must be divisible by 10.')
    # Fixed aspect ratio
    GAME_SIZE = (GAME_WIDTH, GAME_WIDTH * 2)
    # Pixels per block
    BLOCK_SIZE = GAME_WIDTH // 10

class Palette:
    """Contains the specific RGB tuples used for colors in the program. (Treated as an enum but not actually one because it conflicts with PIL)"""
    BLANK = (127, 127, 127)
    I = (0, 255, 255)
    J = (0, 0, 255)
    L = (255, 0, 0)
    S = (0, 255, 0)
    Z = (255, 0, 0)
    O = (255, 255, 0)
    T = (128, 0, 128)

BLANK_SQUARE = PIL.Image.new('RGB', (Constants.BLOCK_SIZE, Constants.BLOCK_SIZE), Palette.BLANK)


def render(field):
    """Converts the list field to a PIL.ImageTk.PhotoImage object and returns it.

    Creates a blank image with size GAME_SIZE. Then iterates through the entire list, placing squares on the image with the appropiate color with the size BLOCK_SIZE. If element is None, it becomes an blank square. If Block, a square with the block's color is used. There SHOULD BE NO Pieces in list, they should be preformated to be Blocks.

    Parameters
    ----------
    field : list
        A 2 dimensional list containing None and/or Block objects to be converted to an image.

    Returns
    -------
    PIL.ImageTk.PhotoImage
        Image of field to be displayed in a tk.canvas.
    """
    global Constants
    global BLANK_SQUARE

    y_pixels = len(field) * Constants.BLOCK_SIZE
    x_pixels = len(field[0]) * Constants.BLOCK_SIZE

    im = PIL.Image.new('RGB', (x_pixels, y_pixels), Palette.BLANK)

    for y, row in enumerate(field):
        for x, block in enumerate(row):
            if block:
                box = (x * Constants.BLOCK_SIZE, y * Constants.BLOCK_SIZE, (x+1) * Constants.BLOCK_SIZE, (y+1) * Constants.BLOCK_SIZE)

                print(box)

                im.paste(block.color, box)

    return PIL.ImageTk.PhotoImage(im)

class App:
    """Controls the tkinter application used as an interface for the game."""
    global tk, PIL

    def __init__(self):
        """Create the tkinter window in which the game is played.

        Returns
        -------
        Tk
            The tk.Tk object that controls the window
        """
        global Constants, Palette

        self.root = tk.Tk()
        self.root.title('Tetris')
        # DEBUG
        self.root['bg'] = 'red'


        # HOLD CANVAS
        self.hold_cvs = tk.Canvas(self.root)
        self.hold_cvs.grid(row=0, column=0, sticky='nesw')
        # DEBUG
        self.hold_cvs['bg'] = 'blue'


        # GAMEFIELD CANVAS
        self.game_cvs = tk.Canvas(self.root)
        self.game_cvs.grid(row=0, column=1, rowspan=2, sticky='nesw')
        # Size
        self.game_cvs.config(width=Constants.GAME_SIZE[0], height=Constants.GAME_SIZE[1])
        # DEBUG
        self.game_cvs['bg'] = 'orange'

        # Init image
        self._game_im = PIL.Image.new('RGB', Constants.GAME_SIZE, Palette.BLANK)
        self._game_im = PIL.ImageTk.PhotoImage(self._game_im)
        self.game_cvs.create_image((Constants.GAME_SIZE[0] / 2, Constants.GAME_SIZE[1] / 2), image=self._game_im)


        # NEXT CANVAS
        self.next_cvs = tk.Canvas(self.root)
        self.next_cvs.grid(row=0, column=2, sticky='nesw')
        # DEBUG
        self.next_cvs['bg'] = 'green'


        # SCORE LABEL
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


    def update_game(self, im):
        """Update the image in the game canvas.

        Clear self.game_cvs. Convert PIL Image to PIL ImageTk and place on game_cvs.

        Parameters
        ----------
        im : PIL.Image
            A PIL Image object
        """
        self.game_cvs.delete('all')

        self._game_im = im
        self.game_cvs.create_image((Constants.GAME_SIZE[0] / 2, Constants.GAME_SIZE[1] / 2), image=self._game_im)

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
    """The main object of the program. Keeps track of a 10x20 grid where the game is played. Contains functions for rendering, piece movement, and coordincate checking. Hosts the App object.

    Instance Variables
    ------------------
    app : App
        The Tk application that interfaces the game to the user.
    current : Piece-like
        The current piece falling.
    gamefield : list
        A 10x23 list describing the placement of all current Blocks and the current Piece falling. The extra 3 top rows are for pieces to start in (not to be display).
    hold : Piece-like
        Variable to hold held piece to be swapped out on command.
    lower_loop : Lower_Piece_Thread
        Object that controls the thread for automatically dropping pieces.
    piece_buffer : Piece_Buffer
        Iterator giving next pieces.
    speed : int
        Current speed in milliseconds. Pieces automatically fall at this speed.
    """

    def __init__(self):
        """Creates the App object. Initializes variables. Calls app.get_ready before starting the game."""
        global Constants
        global App

        self.app = App()

        # self.lower_loop = self.Lower_Piece_Thread()
        print('TO DO: Game.Lower_Piece_Thread')
        self.speed = Constants.START_SPEED

        self.piece_buffer = self.Piece_Buffer()
        self.current = None
        self.hold = None

        # The displayed gamefield is 10x20, the extra 3 rows are where the pieces start from.
        self.gamefield = [[None for x in range(10)] for y in range(23)]

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

    global Palette

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

        self.color = Palette.BLANK

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

        def __init__(self, color, y_offset=0, x_offset=0):
            """Initializes the color and xy_offset variables.

            Parameters
            ----------
            color : int tuple
                A 3 element list with 0 to 255 range decribing the rbg color to be shown when rendered.
            x_offset : int (default = 0)
                The x offset from the top left of the Piece's orientation grid.
            y_offset : int (default = 0)
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

        self.color = Palette.I
class J_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [False, True, False, False],
        [False, True, False, False],
        [True, True, False, False],
        [False, False, False, False]
        ]

        self.color = Palette.J
class L_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [True, False, False, False],
        [True, False, False, False],
        [True, True, False, False],
        [False, False, False, False]
        ]

        self.color = Palette.L
class S_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [False, True, True, False],
        [True, True, False, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = Palette.S
class Z_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [True, True, False, False],
        [False, True, True, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = Palette.Z
class O_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [True, True, False, False],
        [True, True, False, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = Palette.O
class T_Piece(Piece):

    def __init__(self):
        """Initializes the orientation and color variables."""
        self.orientation = [
        [False, True, False, False],
        [True, True, True, False],
        [False, False, False, False],
        [False, False, False, False]
        ]

        self.color = Palette.T

PIECES = (I_Piece, J_Piece, L_Piece, S_Piece, Z_Piece, O_Piece, T_Piece)


if __name__ == '__main__':
    game = Game()

    game.app.run()

    # WHEN TESTING, A LOOP MUST BE USED FOR IMAGES TO DISPLAY
    # input('Enter to quit: ')
