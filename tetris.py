import tkinter as tk
from random import choice
from copy import deepcopy

# DPI Awareness
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

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
    """Contains the specific RGB tuples used for colors in the program. (Treated as an enum but not actually one because it conflicts with PIL)

    Colors obtained from https://colorswall.com/palette/90259/.
    """
    BLANK = (127, 127, 127)
    I = (0, 255, 255)
    J = (0, 0, 255)
    L = (255, 127, 0)
    S = (0, 255, 0)
    Z = (255, 0, 0)
    O = (255, 255, 0)
    T = (128, 0, 128)

BLANK_SQUARE = PIL.Image.new('RGB', (Constants.BLOCK_SIZE, Constants.BLOCK_SIZE), Palette.BLANK)


def init():
    """To be called when game is created. Sets up some global variables including the profiles of each Piece child class."""
    global PIECES

    for p in PIECES:
        p().gen_profile()

# render will place Palette colors according to any pieces in the field
def render(field, piece=None, piece_coord=None):
    """Converts the list field to a PIL.ImageTk.PhotoImage object and returns it.

    Creates a blank image with size GAME_SIZE. Then iterates through the entire list, placing squares on the image with the appropiate color with the size BLOCK_SIZE. If element is None, it becomes an blank square. If Block, a square with the block's color is used. There SHOULD BE NO Pieces in list, they should be preformated to be Blocks.

    Parameters
    ----------
    field : list
        A 2 dimensional list containing None and/or Palette colors to be converted to an image.
    piece : Piece-like (default = None)
        A Piece that should be displayed over the field. Used to display the current piece over gamefield without changing the gamefield itself. If used, piece_coord must also be given. Ignored if None.
    piece_coord : int tuple (default = None)
        The y, x coordinate of where the bottom left corner of piece will be displayed over the field. If used, piece must also be given. Ignored if None.

    Returns
    -------
    PIL.Image
        Image of field.
    """
    global Constants
    global BLANK_SQUARE

    y_pixels = len(field) * Constants.BLOCK_SIZE
    x_pixels = len(field[0]) * Constants.BLOCK_SIZE

    im = PIL.Image.new('RGB', (x_pixels, y_pixels), Palette.BLANK)

    for y, row in enumerate(field):
        for x, block in enumerate(row):
            # block will be either None or a Palette color
            if block:
                box = (x * Constants.BLOCK_SIZE, y * Constants.BLOCK_SIZE, (x+1) * Constants.BLOCK_SIZE, (y+1) * Constants.BLOCK_SIZE)

                # block is a Palette color
                im.paste(block, box)

    if piece:
        for relative_y, row in enumerate(piece.get_blocks()):
            for relative_x, block in enumerate(row):
                if block:
                    # Since coords are from bottm left, the first y is 3 above the piece_coord (when relative_y = 4, it's the row at piece_coord[0])
                    y = relative_y - 3 + piece_coord[0]
                    x = relative_x + piece_coord[1]

                    # If that block falls off the edge, don't draw it
                    try:
                        field[y][x]
                    except IndexError:
                        continue

                    box = (x * Constants.BLOCK_SIZE, y * Constants.BLOCK_SIZE, (x+1) * Constants.BLOCK_SIZE, (y+1) * Constants.BLOCK_SIZE)

                    # block is a Palette color
                    im.paste(piece.color, box)

    return im

class App:
    """Controls the tkinter application used as an interface for the game.

    Instance Variables
    ------------------
    game_cvs : tk.Canvas
        Canvas for displaying the gamefield.
    hold_cvs : tk.Canvas
        Canvas for displaying held tetris pieces.
    next_cvs : tk.Canvas
        Canvas for displaying incoming pieces (pieces in Game.Piece_Buffer).
    root : tk.Tk
        Root of the tk application.
    score_lbl : tk.Label
        Label widget to display current score.
    _game_im : PIL.ImageTk.PhotoImage
        Variable to hold game_cvs's displayed image in memory.
    _game_im_center : int tuple
        2 element tuple giving the center coord of game_cvs for _game_im.
    _hold_im : PIL.ImageTk.PhotoImage
        Variable to hold hold_cvs's displayed image in memory.
    _hold_im_center : int tuple
        2 element tuple giving the center coord of hold_cvs for _hold_im.
    _next_im : PIL.ImageTk.PhotoImage
        Variable to hold next_cvs's displayed image in memory.
    _next_im_center : int tuple
        2 element tuple giving the center coord of next_cvs for _next_im.
    """
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
        self.hold_cvs.grid(row=0, column=0, sticky='new')

        # Size
        hold_size = Constants.BLOCK_SIZE * 4
        self.hold_cvs.config(width=hold_size, height=hold_size)

        # DEBUG
        self.hold_cvs['bg'] = 'blue'

        # Init image
        # Position is the center of the image, hence the / 2
        self._hold_im_center = (hold_size / 2, hold_size / 2)
        self._hold_im = PIL.Image.new('RGB', (hold_size, hold_size), Palette.BLANK)
        self._hold_im = PIL.ImageTk.PhotoImage(self._hold_im)
        self.hold_cvs.create_image(self._hold_im_center, image=self._hold_im)


        # GAMEFIELD CANVAS
        self.game_cvs = tk.Canvas(self.root)
        self.game_cvs.grid(row=0, column=1, rowspan=2, sticky='nesw')

        # Size (More so for readability)
        game_sizex = Constants.GAME_SIZE[0]
        game_sizey = Constants.GAME_SIZE[1]
        self.game_cvs.config(width=game_sizex, height=game_sizey)

        # DEBUG
        self.game_cvs['bg'] = 'orange'

        # Init image
        self._game_im_center = (game_sizex / 2, game_sizey / 2)
        self._game_im = PIL.Image.new('RGB', (game_sizex, game_sizey), Palette.BLANK)
        self._game_im = PIL.ImageTk.PhotoImage(self._game_im)
        self.game_cvs.create_image(self._game_im_center, image=self._game_im)


        # NEXT CANVAS
        self.next_cvs = tk.Canvas(self.root)
        self.next_cvs.grid(row=0, column=2, sticky='new')

        # Size
        next_sizex = Constants.BLOCK_SIZE * 4
        # 5 blocks, 2 lines each, plus a gap between each = 14
        next_sizey = 14 * Constants.BLOCK_SIZE
        self.next_cvs.config(width=next_sizex, height=next_sizey)

        # DEBUG
        self.next_cvs['bg'] = 'green'

        # Init image
        self._next_im_center = (next_sizex / 2, next_sizey / 2)
        self._next_im = PIL.Image.new('RGB', (next_sizex, next_sizey), Palette.BLANK)
        self._next_im = PIL.ImageTk.PhotoImage(self._next_im)
        self.next_cvs.create_image(self._next_im_center, image=self._next_im)


        # SCORE LABEL
        self.score_lbl = tk.Label(self.root, text='Score:\n0')
        self.score_lbl.grid(row=1, column=0, sticky='esw')

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
            The new image to display. Must be PIL.Image not PIL.ImageTk.
        """
        self.game_cvs.delete('all')

        self._game_im = PIL.ImageTk.PhotoImage(new_image)
        self.game_cvs.create_image(self._game_im_center, image=self._game_im)

    def update_next(self, new_image):
        """Update the image in the next canvas.

        Clear self.next_cvs. Convert PIL Image to PIL ImageTk and place on next_cvs.

        Parameters
        ----------
        new_image : PIL.Image
            The new image to display. Must be PIL.Image not PIL.ImageTk.
        """
        self.next_cvs.delete('all')

        self._next_im = PIL.ImageTk.PhotoImage(new_image)
        self.next_cvs.create_image(self._next_im_center, image=self._next_im)

    def update_hold(self, new_image):
        """Update the image in the hold canvas.

        Clear self.hold_cvs. Convert PIL Image to PIL ImageTk and place on hold_cvs.

        Parameters
        ----------
        new_image : PIL.Image
            The new image to display. Must be PIL.Image not PIL.ImageTk.
        """
        self.hold_cvs.delete('all')

        self._hold_im = PIL.ImageTk.PhotoImage(new_image)
        self.hold_cvs.create_image(self._hold_im_center, image=self._hold_im)

class Game:
    """The main object of the program. Keeps track of a 10x20 grid where the game is played. Contains functions for rendering, piece movement, and coordincate checking. Hosts the App object.

    Instance Variables
    ------------------
    app : App
        The Tk application that interfaces the game to the user.
    current : Piece-like
        The current piece falling.
    current_coord : int list
        The y, x coordinate of where the bottom left corner of the current Piece is on the gamefield.
    gamefield : list
        A 10x23 list describing the placement of all current blocks and the current Piece falling. The extra 3 top rows are for pieces to start in (not to be display).
    held : Piece-like
        Variable to hold held piece to be swapped out on command.
    lower_loop : Lower_Piece_Thread
        Object that controls the thread for automatically dropping pieces.
    piece_buffer : Piece_Buffer
        Iterator giving next pieces.
    speed : int
        Current speed in milliseconds. Pieces automatically fall at this speed.
    _already_held : bool
        Becomes true when the user holds a piece (calls hold). If True, this prevents the user to hold again until the next piece.
    """

    def __init__(self):
        """Creates the App object. Initializes variables. Calls app.get_ready before starting the game."""
        global Constants
        global App

        self.app = App()

        # self.lower_loop = self.Lower_Piece_Thread()
        print('TO DO: Game.Lower_Piece_Thread')
        self.speed = Constants.START_SPEED

        self.piece_buffer = self.Piece_Buffer(self.app)
        self.current = None
        self.current_coord = [3, 3]    # y, x
        self.held = None

        # The displayed gamefield is 10x20, the extra 3 rows are where the pieces start from.
        self.gamefield = [[None for x in range(10)] for y in range(23)]

        # Show instructions and then play
        self.app.get_ready()
        # self.start()

    def hold(self):
        """Swap out the Piece in the current and hold variables. Event binding for hold button.

        If hold is None (first held piece), save current Piece to it and replace current with the next Piece. Change the piece position to the top. Update hold canvas and
        """
        global PIL
        global Constants
        global Palette

        # If this is the first held piece
        if self.held is None:
            self.held = self.current
            self.current = next(self.piece_buffer)
        # Prevent user from holding again before next piece
        elif self._already_held:
            return None
        else:
            new_hold = self.current
            self.current = self.held
            self.held = new_hold

        self._already_held = True
        print('TO DO: Game.hold must reset piece position to top')

        # Update hold canvas
        size = 4 * Constants.BLOCK_SIZE
        im = PIL.Image.new('RGB', (size, size), Palette.BLANK)

        box = (0, Constants.BLOCK_SIZE, size, size - Constants.BLOCK_SIZE)
        im.paste(self.held.profile, box)

        self.app.update_hold(im)

    def update_cvs(self):
        """Update the image of the gamefield in the tk application."""
        global render

        im = render(self.gamefield[3:], self.current, self.current_coord)
        self.app.update_game(im)

    class Piece_Buffer:
        """Iterator object that generates tetris pieces. Always keeps 5 pieces.

        Instance Variables
        ------------------
        pieces
            A 5 element list describing the coming squence of pieces.
        """

        def __init__(self, app):
            """Initialize the pieces list and generate the initial pieces.

            Parameters
            ----------
            app : App
                The app instance being used in the game instance. Needed for update_cvs to update the next canvas in the tk app.
            """
            self.pieces = []
            self.app = app

            for i in range(5):
                self.gen_new_piece()

            self.update_cvs()

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
            global PIL
            global Constants
            global Palette

            sizex = 4 * Constants.BLOCK_SIZE
            # 14 is 2 lines for each Piece with a gap between each
            sizey = 14 * Constants.BLOCK_SIZE

            im = PIL.Image.new('RGB', (sizex, sizey), Palette.BLANK)

            y = 0
            for i, p in enumerate(self.pieces):
                height = y + (2 * Constants.BLOCK_SIZE)

                box = (0, y, sizex, height)
                im.paste(p.profile.copy(), box)

                # Add gap between profiles
                y = height + Constants.BLOCK_SIZE

            self.app.update_next(im)

        def __str__(self):
            """Creates a string representation of the coming pieces for debugging."""
            fin = ''
            for piece in self.pieces:
                p = str(piece) + '\n'
                fin += p

            return fin


class Piece:
    """Base class for tetris piece. Can be used as an iterator to get Block objects.

    Class variables
    ---------------
    color : int tuple
        A 3 element list with 0 to 255 range decribing the rbg color to be shown when Blocks are rendered.
    profile : PIL.Image
        An image of the piece on it's side to be used in hold and next images.
    _init_orient : bool list
        A 4 by 4 list of booleans describing the relative positions of all Blocks in the initial orientation.

    Instance variables
    ------------------
    orientation : bool list
        A 4 by 4 list of booleans describing the relative positions of all blocks.
    """
    global Palette

    _init_orient = [[False for x in range(4)] for y in range(4)]
    color = Palette.BLANK

    profile = None

    def __init__(self, orientation=None):
        """Initializes the orientation and color variables.

        Parameters
        ----------
        orientation : bool list (default None)
            An optional starting orientation. Used when rotating a piece so that it's new position can be tested before replacing origional orientation. A 4 by 4 list of booleans describing the relative positions of all Blocks.
        """
        if orientation is None:
            global deepcopy
            self.orientation = deepcopy(self._init_orient)
        else:
            self.orientation = orientation


    def rotate_cw(self):
        """Rotates the Piece clockwise.

        Calculates a new orientation grid and returns a new Piece-like object (same type as this one) with that orientation.

        Returns
        -------
        Piece-like
            The same type of piece but with an orientation grid rotated clockwise.
        """
        new_orientation = [[False for x in range(4)] for y in range(4)]

        # Rotate
        for y, row in enumerate(self.orientation):
            for x, block in enumerate(row):
                new_orientation[x][3-y] = block

        new_orientation = self._push_topleft(new_orientation)

        return self.__class__(new_orientation)

    def rotate_ccw(self):
        """Rotates the Piece clockwise.

        Calculates a new orientation grid and returns a new Piece-like object (same type as this one) with that orientation.

        Returns
        -------
        Piece-like
            The same type of piece but with an orientation grid rotated clockwise.
        """
        new_orientation = [[False for x in range(4)] for y in range(4)]

        # Rotate
        for y, row in enumerate(self.orientation):
            for x, block in enumerate(row):
                new_orientation[3-x][y] = block

        new_orientation = self._push_topleft(new_orientation)

        return self.__class__(new_orientation)

    def _push_topleft(self, orient):
        """Pushes blocks in orient as far to the topleft as possible.

        Parameters
        ----------
        orient : bool list
            The 4 by 4 array of booleans describing relative block positions

        Returns
        -------
        bool list
            The same 4 by 4 array but with the contents pushed to the top left.
        """
        # Check for blank rows, move up
        while True:
            try:
                for block in orient[0]:
                    if block:
                        raise StopIteration
                blank = orient.pop(0)
                orient.append(blank)
            except StopIteration:
                break

        # Check for blank columns, move left
        # for row in orient:
        #     if row[0]:
        #         break
        # else:
        #     for row in orient:
        #         row.append(row.pop(0))

        return orient


    def get_blocks(self):
        """Creates Block objects representing the current orientation.

        Cycles through the orientation grid and where True, creates a Block object and puts it in a list to iterate.

        Returns
        -------
        list
            Returns a 4 by 4 grid with None in empty spots and a Palette color in place of where blocks would be.
        """
        blocks = [[None for x in range(4)] for y in range(4)]

        for y, row in enumerate(self.orientation):
            for x, block in enumerate(row):
                if block:
                    blocks[y][x] = self.color

        return blocks

    def __str__(self):
        """Creates a string representation of the Piece for debuging."""
        fin = 'Color: ' + str(self.color) + '\n'

        for row in self.orientation:
            fin += str(row) + '\n'

        return fin

class I_Piece(Piece):

    _init_orient = [
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False]
    ]
    color = Palette.I

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        p = self.rotate_cw()

        # After rotation, the block should be oriented to fit in a 2 by 4 image.
        self.__class__.profile = render(p.get_blocks()[:2])
class J_Piece(Piece):

    _init_orient = [
        [False, True, False, False],
        [False, True, False, False],
        [True, True, False, False],
        [False, False, False, False]
    ]
    color = Palette.J

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        p = self.rotate_cw()

        # After rotation, the block should be oriented to fit in a 2 by 4 image.
        self.__class__.profile = render(p.get_blocks()[:2])
class L_Piece(Piece):

    _init_orient = [
        [True, False, False, False],
        [True, False, False, False],
        [True, True, False, False],
        [False, False, False, False]
    ]
    color = Palette.L

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        p = self.rotate_ccw()

        # After rotation, the block should be oriented to fit in a 2 by 4 image.
        self.__class__.profile = render(p.get_blocks()[:2])
class S_Piece(Piece):

    _init_orient = [
        [False, True, True, False],
        [True, True, False, False],
        [False, False, False, False],
        [False, False, False, False]
    ]
    color = Palette.S

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        # After rotation, the block should be oriented to fit in a 2 by 4 image.
        self.__class__.profile = render(self.get_blocks()[:2])
class Z_Piece(Piece):

    _init_orient = [
        [True, True, False, False],
        [False, True, True, False],
        [False, False, False, False],
        [False, False, False, False]
    ]
    color = Palette.Z

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        # After rotation, the block should be oriented to fit in a 2 by 4 image.
        self.__class__.profile = render(self.get_blocks()[:2])
class O_Piece(Piece):

    _init_orient = [
        [True, True, False, False],
        [True, True, False, False],
        [False, False, False, False],
        [False, False, False, False]
    ]
    color = Palette.O

    def rotate_cw(self):
        """Overrides Piece.rotate_cw. Returns self to avoid issues."""
        return self
    def rotate_ccw(self):
        """Overrides Piece.rotate_cw. Returns self to avoid issues."""
        return self

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        # After rotation, the block should be oriented to fit in a 2 by 4 image.
        self.__class__.profile = render(self.get_blocks()[:2])
class T_Piece(Piece):

    _init_orient = [
        [False, True, False, False],
        [True, True, True, False],
        [False, False, False, False],
        [False, False, False, False]
    ]
    color = Palette.T

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        # After rotation, the block should be oriented to fit in a 2 by 4 image.
        self.__class__.profile = render(self.get_blocks()[:2])

PIECES = (I_Piece, J_Piece, L_Piece, S_Piece, Z_Piece, O_Piece, T_Piece)


def freeze_test(game):
    """Uses console input to move control movement manually.

    Parameters
    ----------
    game : Game
        The instance of Game being played.
    """
    game.current = next(game.piece_buffer)

    print('z for quit, h for hold, s for down, w for up, a for left, d for right, q for ccw rotate, e for cw rotate.\n')

    while True:
        inp = input(' - ')

        if 'z' in inp:
            break
        elif 'h' in inp:
            game.hold()
            game._already_held = False
        elif 'w' in inp:
            game.current_coord[0] -= 1
        elif 's' in inp:
            game.current_coord[0] += 1
        elif 'a' in inp:
            game.current_coord[1] -= 1
        elif 'd' in inp:
            game.current_coord[1] += 1
        elif 'q' in inp:
            game.current = game.current.rotate_ccw()
        elif 'e' in inp:
            game.current = game.current.rotate_cw()

        game.update_cvs()


if __name__ == '__main__':
    init()
    game = Game()

    freeze_test(game)

    # WHEN TESTING, A LOOP MUST BE USED FOR IMAGES TO DISPLAY
    # input('Enter to quit: ')
