import tkinter as tk
from tkinter import messagebox
from threading import Timer
from random import choice
from copy import deepcopy

# DPI Awareness
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    print('There was a problem setting DPI Awareness')

# Import PIL
try:
    import PIL.Image
    import PIL.ImageTk
    import PIL.ImageDraw
except ModuleNotFoundError:
    print('\n-----')
    print("This program requires the Python library 'Pillow'. Use pip or pipenv install pillow to download the library (virtual environment is encouraged).")
    print('-----')
    exit()


# CONSTANTS
class Constants:
    """Enum of global constants. (Not actually an enum because it conflicts with PIL)"""
    # MANUALLY ADJUST
    # In milliseconds:
    START_SPEED = 1.0
    # Multiplied by the speed
    SPEED_STEP = 2 / 3
    # Lines to clear before speed changes
    LINES_SPEED_STEP = 4

    # In pixels:
    # Should be divisible by 10
    GAME_WIDTH = 400
    # Border size
    BD_SIZE = 5


    # DON'T MANUALLY ADJUST
    if GAME_WIDTH % 10:
        raise ValueError('GAME_WIDTH must be divisible by 10.')
    # Fixed aspect ratio
    GAME_SIZE = (GAME_WIDTH, GAME_WIDTH * 2)
    # Pixels per block
    BLOCK_SIZE = GAME_WIDTH // 10

class Palette:
    """Contains the specific RGB tuples used for colors in the program. (Treated as an enum but not actually one because it conflicts with PIL)

    Colors obtained from https://colorswall.com/palette/90259/.
    """

    def _get_blank_hex(blank):
        full = ''
        for channel in blank:
            val = hex(channel)[2:]
            while len(val) < 2:
                val = '0' + val
            full += val
        return full

    BLANK = (127, 127, 127)
    BLANK_HEX = '#' + _get_blank_hex(BLANK)

    GRIDLINE = (0, 0, 0)

    I = (0, 255, 255)
    J = (0, 0, 255)
    L = (255, 127, 0)
    S = (0, 255, 0)
    Z = (255, 0, 0)
    O = (255, 255, 0)
    T = (128, 0, 128)

generated_squares = dict()


def init():
    """To be called when game is created. Sets up some global variables including the profiles of each Piece child class."""
    global PIECES

    for p in PIECES:
        p().gen_profile()

def block_render(color=None, block=False, grid=False):
    """Renders the image of a single square.

    Parameters
    ----------
    color : int tuple (default = None)
        The rgb value of the square. If None, Palette.BLANK will be used
    block : bool (default = False)
        Determines if the block style overlay should be used.
    grid : bool (default = False)
        Determines if the gridline overlay should be used.

    Returns
    -------
    PIL.Image
        Image of the square.
    """
    global PIL
    global Constants
    global Palette

    size = Constants.BLOCK_SIZE

    if not color:
        color = Palette.BLANK

    square = PIL.Image.new('RGB', (size, size), color)

    im_draw = PIL.ImageDraw.Draw(square, 'RGB')
    max_index = size-1

    if grid:
        line_list = [
            # (x, y)
            (0, max_index),
            (max_index, max_index),
            (max_index, 0)
        ]
        im_draw.line(line_list, fill=Palette.GRIDLINE)

    if block:
        border = size * 0.2

        line_list = [
            (0, 0),
            (0, max_index),
            (border, max_index - border),
            (border, border),
            (0, 0),
            (max_index, 0),
            (max_index - border, border),
            (border, border)
        ]
        im_draw.line(line_list, fill=Palette.GRIDLINE)

        line_list = [
            (max_index, max_index),
            (max_index, 0),
            (max_index - border, border),
            (max_index - border, max_index - border),
            (max_index, max_index),
            (0, max_index),
            (border, max_index - border),
            (max_index - border, max_index - border)
        ]
        im_draw.line(line_list, fill=Palette.GRIDLINE)

    return square

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
    global generated_squares
    global block_render

    y_pixels = len(field) * Constants.BLOCK_SIZE
    x_pixels = len(field[0]) * Constants.BLOCK_SIZE

    im = PIL.Image.new('RGB', (x_pixels, y_pixels), Palette.BLANK)

    for y, row in enumerate(field):
        for x, block in enumerate(row):
            box = (x * Constants.BLOCK_SIZE, y * Constants.BLOCK_SIZE, (x+1) * Constants.BLOCK_SIZE, (y+1) * Constants.BLOCK_SIZE)

            try:
                # Use cached image if present
                square = generated_squares[block].copy()
            except KeyError:
                # Generates and caches block image
                if block:
                    square = block_render(block, block=True)
                else:
                    # Block is an empty square
                    square = block_render(grid=True)
                generated_squares[block] = square.copy()

            im.paste(square, box)

    if piece:
        for relative_y, row in enumerate(piece.get_blocks()):
            # Since coords are from bottm left, the first y is 3 above the piece_coord (when relative_y = 4, it's the row at piece_coord[0])
            y = relative_y + piece_coord[0] - 3

            for relative_x, block in enumerate(row):
                if block:
                    x = relative_x + piece_coord[1]

                    # If that block falls off the edge, don't draw it
                    try:
                        field[y][x]
                    except IndexError:
                        continue

                    box = (x * Constants.BLOCK_SIZE, y * Constants.BLOCK_SIZE, (x+1) * Constants.BLOCK_SIZE, (y+1) * Constants.BLOCK_SIZE)

                    try:
                        # Use cached image if present
                        square = generated_squares[block].copy()
                    except KeyError:
                        # Generates and caches block image
                        if block is None:
                            # Block is an empty square
                            square = block_render(grid=True)
                        else:
                            square = block_render(block, block=True)
                        generated_squares[block] = square.copy()

                    im.paste(square, box)

    return im


class App:
    """Controls the tkinter application used as an interface for the game.

    Instance Variables
    ------------------
    game_cvs : tk.Canvas
        Canvas for displaying the gamefield.
    hold_cvs : tk.Canvas
        Canvas for displaying held tetris pieces.
    info_lbl : tk.Label
        Label widget to display current score, speed, and lines completed.
    next_cvs : tk.Canvas
        Canvas for displaying incoming pieces (pieces in Game.Piece_Buffer).
    root : tk.Tk
        Root of the tk application.
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

    def __init__(self, game):
        """Create the tkinter window in which the game is played.

        Parameters
        ----------
        game: Game
            The instance of game that is being played. Needed in order to bind events to the tk application and to bind game.lose to when the window is closed.

        Returns
        -------
        Tk
            The tk.Tk object that controls the window
        """
        global Constants, Palette


        self.root = tk.Tk()
        self.root.title('Tetris')


        # HOLD CANVAS
        self.hold_cvs = tk.Canvas(self.root)
        self.hold_cvs.grid(row=0, column=0, sticky='new')

        # Size
        hold_size = Constants.BLOCK_SIZE * 4
        self.hold_cvs.config(width=hold_size, height=hold_size)

        # Appearance
        self.hold_cvs['relief'] = 'sunken'
        self.hold_cvs['bd'] = Constants.BD_SIZE

        # Init image
        # Position is the center of the image, hence the / 2
        self._hold_im_center = ((hold_size / 2) + Constants.BD_SIZE, (hold_size / 2) + Constants.BD_SIZE)
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

        # Appearance
        self.game_cvs['relief'] = 'sunken'
        self.game_cvs['bd'] = Constants.BD_SIZE

        # Init image
        self._game_im_center = ((game_sizex / 2) + Constants.BD_SIZE, (game_sizey / 2) + Constants.BD_SIZE)
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

        # Appearance
        self.next_cvs['relief'] = 'sunken'
        self.next_cvs['bd'] = Constants.BD_SIZE

        # Init image
        self._next_im_center = ((next_sizex / 2) + Constants.BD_SIZE, (next_sizey / 2) + Constants.BD_SIZE)
        self._next_im = PIL.Image.new('RGB', (next_sizex, next_sizey), Palette.BLANK)
        self._next_im = PIL.ImageTk.PhotoImage(self._next_im)
        self.next_cvs.create_image(self._next_im_center, image=self._next_im)


        # SCORE LABEL
        self.info_lbl = tk.Label(self.root, text='init text')
        self.info_lbl.grid(row=1, column=0, sticky='nesw')
        self.info_lbl['fg'] = 'white'


        # ON CLOSE PROTOCOL
        def on_closing():
            """Protocol handler for when the window should close."""
            game.stop()
        self.root.protocol("WM_DELETE_WINDOW", on_closing)


        # FINAL SETTINGS
        self.set_background(Palette.BLANK_HEX)
        self.update_lbl(0, 0, Constants.START_SPEED)

        # Disable window resizing
        self.root.resizable(False, False)

        self.make_bindings(game)

    def make_bindings(self, game):
        """Setup all event bindings needed in the program.

        Parameters
        ----------
        game: Game
            The instance of game that is being played. Needed in order to bind events to the tk application.
        """
        # WASD Controls
        self.root.bind_all('<s>', game.down)
        self.root.bind_all('<space>', game.hard_drop)

        self.root.bind_all('<a>', game.left)
        self.root.bind_all('<d>', game.right)

        self.root.bind_all('<q>', game.rotate_ccw)
        self.root.bind_all('<e>', game.rotate_cw)

        self.root.bind_all('<w>', game.hold)

        self.root.bind_all('<p>', game.lose)

        # Arrow Controls
        self.root.bind_all('<Down>', game.down)

        self.root.bind_all('<Left>', game.left)
        self.root.bind_all('<Right>', game.right)

        self.root.bind_all('<Up>', game.rotate_cw)

        self.root.bind_all('<z>', game.hold)

    def set_background(self, color, container=None):
        """Recursively sets the background of every widget to color.

        Parameters
        ----------
        color : int tuple
            The rgb color to set the backgrounds to.
        container : Tk object (default = None)
            The container to look through for widgets and more containers to change the background of.
        """
        if container is None:
            container = self.root

        container.config(bg=color)

        for child in container.winfo_children():
            if child.winfo_children():
                # child has children, go through its children
                self.set_background(color, child)
            else:
                child.config(bg=color)


    def start(self, call_me):
        """Starts the event loop and calls get_ready to display instructions. call_me is a function that will be called once the user has closed the get_ready popup."""

        def get_ready():
            """Show a pop-up window with instructions and a start button."""
            global messagebox

            message = "Welcome to my homebrew Python version of Tetris.\n"
            message += "Everyone who doesn't live under a rock knows the rules, so I'm not going to explain them here. However the controls I will explain.\n\n"

            message += "Controls:\n"
            message += "   Move left/right - A / D or left / right arrows\n"
            message += "   Rotate left/right - Q / E or up arrow (only rotate right)\n"
            message += "   Down - S or down arrow\n"
            message += "   Hard drop - Space\n"
            message += "   Hold - W or Z\n"
            message += "   Quit - P\n\n"

            message += "Made by Carson Jones (2021).\n"
            message += "Source code: https://github.com/DJCubed12/Tetris"

            messagebox.showinfo('Instructions', message)

            call_me()

        self.root.after_idle(get_ready)
        self.root.mainloop()



        call_me()

    def play_again(self, score, lines, speed):
        """The user has lost. Display stats and ask for another round. If yes return True for Game."""
        global messagebox

        message = "GAME OVER\n\n"

        message += f"Final Stats:\n"
        message += f"   Score - {score}\n"
        message += f"   Lines - {lines}\n"
        message += f"   Speed - {(1/speed):.3f} b/s\n\n"

        message += f"Play Again?\n"

        return messagebox.askyesno('Play Again?', message)


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

    def update_lbl(self, score, lines, speed):
        """Update the info label to reflect the new score, lines completed, and speed.

        Parameters
        ----------
        score : int
            The current score the user has.
        lines : int
            The total number of lines completed.
        speed : int
            The current speed.
        """
        speed = 1 / speed

        new_score = f'Score:\n{score}\n\n'
        new_lines = f'Lines:\n{lines}\n\n'
        new_speed = f'Speed:\n{speed:.3f} b/s'

        self.info_lbl['text'] = new_score + new_lines + new_speed

class Game:
    """The main object of the program. Keeps track of a 10x20 grid where the game is played. Contains functions for rendering, piece movement, and coordincate checking. Hosts the App object.

    Instance Variables
    ------------------
    app : App
        The Tk application that interfaces the game to the user.
    current : Piece-like
        The current piece falling.
    current_coord : int list
        The y, x coordinate of where the bottom left corner of the current Piece is on the gamefield. Next Pieces should start at [0, 3].
    drop_timer : RepeatedTimer
        The Timer object that is ran in a different thread that calls drop_loop periodically.
    gamefield : list
        A 10x23 list describing the placement of all current blocks and the current Piece falling. The extra 3 top rows are for pieces to start in (not to be display).
    held : Piece-like
        Variable to hold held piece to be swapped out on command.
    lines_complete : int
        Total number of lines completed.
    piece_buffer : Piece_Buffer
        Iterator giving next pieces.
    score : int
        Score the user has earned.
    speed : int
        Current speed in milliseconds. Pieces automatically fall at this speed.
    _already_held : bool
        Becomes true when the user holds a piece (calls hold). If True, this prevents the user to hold again until the next piece.
    _lines_step_counter : int
        Number of lines left until speed changes. Resets to Constants.LINES_SPEED_STEP.
    """

    def __init__(self, app=None):
        """Creates the App object. Initializes variables. Calls app.get_ready before starting the game."""
        global RepeatedTimer
        global Constants
        global App

        if app is None:
            app = App(self)
        self.app = app

        # The displayed gamefield is 10x20, the extra 3 rows are where the pieces start from.
        self.gamefield = [[None for x in range(10)] for y in range(23)]

        self.score = 0
        self.speed = Constants.START_SPEED
        self.lines_complete = 0
        self._lines_step_counter = Constants.LINES_SPEED_STEP
        self.drop_timer = RepeatedTimer(self.speed, self.down)

        self.piece_buffer = self.Piece_Buffer(self.app)
        self.current = None
        self.current_coord = [0, 3]    # y, x
        self.held = None

        # Show instructions and then play
        self.start()

    def start(self):
        """Starts both the drop loop and tk event loop and creates the first piece."""

        self.current = next(self.piece_buffer)

        self.update_cvs()

        # print('DEBUG: self.drop_timer.start not passed [Game.start]')
        # self.app.start(lambda: None)
        self.app.start(self.drop_timer.start)

    def stop(self, event=None):
        """Stops the game and the tk interface."""

        self.drop_timer.stop()
        self.app.root.destroy()

    def lose(self, event=None):
        """Called once the user has lost the game. Asks the user to play again. If not calls stop to end everything."""
        self.drop_timer.stop()

        if self.app.play_again(self.score, self.lines_complete, self.speed):
            self.__init__(self.app)
        else:
            self.stop()


    def hold(self, event=None):
        """Swap out the Piece in the current and hold variables. Event binding for hold button.

        If hold is None (first held piece), save current Piece to it and replace current with the next Piece. Change the piece position to the top. Update hold canvas and
        """
        global PIL
        global Constants
        global Palette
        global render

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
        self.current_coord = [0, 3]

        # Update hold canvas
        size = 4 * Constants.BLOCK_SIZE
        im = PIL.Image.new('RGB', (size, size), Palette.BLANK)

        blank_row = render([[None for x in range(4)]])
        box = (0, 0, size, Constants.BLOCK_SIZE)
        im.paste(blank_row.copy(), box)

        box = (0, Constants.BLOCK_SIZE, size, size - Constants.BLOCK_SIZE)
        im.paste(self.held.profile, box)

        box = (0, size - Constants.BLOCK_SIZE, size, size)
        im.paste(blank_row.copy(), box)

        self.app.update_hold(im)
        self.update_cvs()

    def down(self, event=None):
        """Moves the piece down if allowed by check_move, otherwise, make_permanent."""
        new_coord = [self.current_coord[0] + 1, self.current_coord[1]]
        all_clear = self.check_move(self.current, new_coord)

        if all_clear:
            self.current_coord = new_coord
        else:
            self.make_permanent()

        self.update_cvs()

    def hard_drop(self, event=None):
        """Drops the piece as far as possible and places it there (using make_permanent)."""
        new_coord = self.current_coord
        all_clear = True
        while all_clear:
            new_coord[0] += 1
            all_clear = self.check_move(self.current, new_coord)
            # If that drop was not allowed, loop will be dropped

        # Undo that last drop (it was not allowed)
        new_coord[0] -= 1
        self.current_coord = new_coord

        self.make_permanent()

        self.update_cvs()

    def right(self, event=None):
        """Moves the piece right if allowed by check_move, otherwise, make_permanent."""
        new_coord = [self.current_coord[0], self.current_coord[1] + 1]
        all_clear = self.check_move(self.current, new_coord)

        if all_clear:
            self.current_coord = new_coord

        self.update_cvs()

    def left(self, event=None):
        """Moves the piece left if allowed by check_move, otherwise, make_permanent."""
        new_coord = [self.current_coord[0], self.current_coord[1] - 1]
        all_clear = self.check_move(self.current, new_coord)

        if all_clear:
            self.current_coord = new_coord

        self.update_cvs()

    def rotate_cw(self, event=None):
        """Rotates the piece clockwise if allowed by check_move, otherwise, make_permanent."""
        new_orient = self.current.rotate_cw()
        all_clear = self.check_move(new_orient, self.current_coord)

        if all_clear:
            self.current = new_orient

        self.update_cvs()

    def rotate_ccw(self, event=None):
        """Rotates the piece counter-clockwise if allowed by check_move, otherwise, make_permanent."""
        new_orient = self.current.rotate_ccw()
        all_clear = self.check_move(new_orient, self.current_coord)

        if all_clear:
            self.current = new_orient

        self.update_cvs()


    def check_move(self, new_piece, new_coord):
            """Checks to see if the new position will conflict with the current gamefield. If so return True.

            Checks for when the block of a piece has the same coord as an existing block in the gamefield. Also checks for if a block of the piece would be outside the bounds of the gamefield.

            Parameters
            ----------
            new_piece : Piece-like
                The Piece being tested at position new_coord.
            new_coord : int list
                The new y, x coordinate of the bottom left corner of new_piece's orientation grid.

            Returns
            -------
            bool
                False if the new position would hit a pre-existing block, otherwise True.
            """
            for relative_y, row in enumerate(new_piece.get_blocks()):
                y = relative_y + new_coord[0]
                for relative_x, block in enumerate(row):
                    # If the piece has a block in this part of its orientation grid. If not, no point of checking (empty space).
                    if block:
                        x = relative_x + new_coord[1]
                        if x < 0:
                            # Block is outside the left wall. Must check because python will interpret [-1] differently
                            return False

                        try:
                            # If this block is outside the bounds of the gamefield, IndexError is raised.
                            if self.gamefield[y][x] is not None:
                                # There's a block on the gamefield here, this is a conflict.
                                return False
                        except IndexError:
                            # Block is outside the gamefield, this is a conflict.
                            return False

            # No conflict detected, movement is ok
            return True

    def make_permanent(self):
        """Permanently places the current piece at it's current position, checks for lines completed, and gets next piece.

        Goes through the current piece's blocks and sets their corresponding place in the gamefield to the piece's color. Then the current piece is the next piece in the Piece Buffer and the current coordinate is reset. Then checks for and clears lines completed using check_lines and finally updates the canvas.
        """
        for relative_y, row in enumerate(self.current.get_blocks()):
            y = relative_y + self.current_coord[0]
            for relative_x, block in enumerate(row):
                if block:
                    x = self.current_coord[1] + relative_x
                    # Place block
                    self.gamefield[y][x] = self.current.color

        self.current = next(self.piece_buffer)
        self.current_coord = [0, 3]
        # Allow hold button again
        self._already_held = False

        self.check_lines()

        self.update_cvs()

    def check_lines(self):
        """Finds completed lines, clears them, moves everything down accordingly, and updates the score.

        Checks each line of the gamefield from the bottom up. If any lines were completed, they are deleted and a new empty line is added to the top of the gamefield, shuffling everything down. Updates score and speed accordingly.
        """
        # lines is a log of the index of completed lines
        lines = []
        for y, row in enumerate(self.gamefield):
            for block in row:
                if not block:
                    # There is a gap, stop checking this row, move on
                    break
            else:
                # No gap detected, this is a complete line
                lines.append(y)

        if len(lines):
            for line in lines:
                del self.gamefield[line]
                self.gamefield.insert(0, [None for x in range(10)])

            self.score_manager(len(lines))

        # Check for loss after completing and clearing any lines
        for block in self.gamefield[2]:
            if block:
                self.lose()

    def score_manager(self, lines):
        """Manages the changes and additions to the user's score including updating the tk label and changing the speed.

        Parameters
        ----------
        lines : int
            Number of lines that have been cleared.
        """
        self.score += 100 * lines
        self.lines_complete += lines
        if lines == 4:
            self.score += 100

        self._lines_step_counter -= lines
        if self._lines_step_counter <= 0:
            global Constants

            # Allow excess lines to overflow to next counter
            self._lines_step_counter += Constants.LINES_SPEED_STEP
            self.speed *= Constants.SPEED_STEP
            self.drop_timer.interval = self.speed

        self.app.update_lbl(self.score, self.lines_complete, self.speed)

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

            # Place a blank row of grid squares between each profile
            blank_row = render([[None for x in range(4)]])
            y = 2
            for i in range(4):
                box = (0, y * Constants.BLOCK_SIZE, sizex, (y + 1) * Constants.BLOCK_SIZE)
                im.paste(blank_row.copy(), box)

                y += 3

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


class RepeatedTimer:
    """Uses threading.Timer to repeatedly use another thread to call a function every interval seconds.

    Stolen from https://www.py4u.net/discuss/10170 (Answer #3)
    """
    global Timer

    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False

        # Auto-run:
        # self.start()

    def _run(self):
        self.is_running = False
        try:
            self.function(*self.args, **self.kwargs)
            self.start()
        except RuntimeError:
            print('RUNETIME ERROR: Shutting down drop loop.')

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        try:
            self._timer.cancel()
        except AttributeError:
            # Timer was never created
            pass
        self.is_running = False


class Piece:
    """Base class for tetris piece.

    Class variables
    ---------------
    color : int tuple
        A 3 element list with 0 to 255 range decribing the rbg color to be shown when Blocks are rendered.
    profile : PIL.Image
        An image of the piece on it's side to be used in hold and next images.
    _init_orient : bool list
        A 4 by 4 list of booleans describing the relative positions of all Blocks in the initial orientation.
    _rot_for_profile : bool
        Tells if gen_profile should rotate before generating the profile. 1 for clockwise rotation, -1 for counter-clockwise, 0 for no rotation.

    Instance variables
    ------------------
    orientation : bool list
        A matrix of booleans describing the relative positions of all blocks.
    _matrix_size : int
        The size (same for x and y) of this piece's orient matrix.
    """
    global Palette

    color = Palette.BLANK

    profile = None
    _rot_for_profile = 0

    _init_orient = [[False for x in range(4)] for y in range(4)]

    _empty_orient = lambda self: [[False for x in range(self._matrix_size)] for y in range(self._matrix_size)]

    def __init__(self, orientation=None):
        """Initializes the orientation and color variables.

        Parameters
        ----------
        orientation : bool list (default None)
            An optional starting orientation. Used when rotating a piece so that it's new position can be tested before replacing origional orientation. A matrix of booleans describing the relative positions of all blocks.
        """
        if orientation is None:
            global deepcopy
            self.orientation = deepcopy(self._init_orient)
        else:
            self.orientation = orientation

        self._matrix_size = len(self._init_orient)


    def rotate_cw(self):
        """Rotates the Piece clockwise.

        Calculates a new orientation grid and returns a new Piece-like object (same type as this one) with that orientation.

        Returns
        -------
        Piece-like
            The same type of piece but with an orientation grid rotated clockwise.
        """
        new_orientation = self._empty_orient()

        # Rotate
        for y, row in enumerate(self.orientation):
            for x, block in enumerate(row):
                # self._matrix_size-1 is the index of the end of the matrix
                new_orientation[x][self._matrix_size-1-y] = block

        return self.__class__(new_orientation)

    def rotate_ccw(self):
        """Rotates the Piece clockwise.

        Calculates a new orientation grid and returns a new Piece-like object (same type as this one) with that orientation.

        Returns
        -------
        Piece-like
            The same type of piece but with an orientation grid rotated clockwise.
        """
        new_orientation = self._empty_orient()

        # Rotate
        for y, row in enumerate(self.orientation):
            for x, block in enumerate(row):
                # self._matrix_size-1 is the index of the end of the matrix
                new_orientation[self._matrix_size-1-x][y] = block

        return self.__class__(new_orientation)


    def get_blocks(self):
        """Creates Block objects representing the current orientation.

        Cycles through the orientation grid and where True, creates a Block object and puts it in a list to iterate.

        Returns
        -------
        list
            Returns a matrix corresponding to the orient with None in empty spots and a Palette color in place of where blocks would be.
        """
        blocks = self._empty_orient()

        for y, row in enumerate(self.orientation):
            for x, block in enumerate(row):
                if block:
                    blocks[y][x] = self.color

        return blocks

    def gen_profile(self):
        """Creates a PIL.Image showing the piece on its side to be displayed in hold and next canvases."""
        global render

        # After possible rotation, the block should be oriented to fit in a 2 by 4 image.
        if self._rot_for_profile == 1:
            p = self.rotate_cw()
        elif self._rot_for_profile == -1:
            p = self.rotate_ccw()
        else:
            p = self

        p = p.get_blocks()[:2]
        # If not a 4 by 4 matrix, add empty columns to fit the 2 by 4 image.
        if len(p[0]) < 4:
            for row in p:
                row.append(None)

        self.__class__.profile = render(p)

    def __str__(self):
        """Creates a string representation of the Piece for debuging."""
        fin = 'Color: ' + str(self.color) + '\n'

        for row in self.orientation:
            fin += str(row) + '\n'

        return fin

class Two_State_Piece(Piece):
    """A tetris piece that specifically has two states (rotation states) and has altered rotation functions that abuse this fact.

    Class Variables
    ---------------
    first_state : bool
        Tells which state the piece is in. True if using _init_orient (first state), False if using _alt_orient (second state).
    """

    # Inherited Pieces should replace _init_orient and:
    _alt_orient = [[False for x in range(4)] for y in range(4)]

    def __init__(self, init_orientation=True):
        """Initializes the orientation and color variables.

        Parameters
        ----------
        init_orientation : bool list (default True)
            Determines if the piece is in first state (_init_orient) or second state (_alt_orient). True for first state, False for second.
        """
        global deepcopy
        if init_orientation:
            self.orientation = deepcopy(self._init_orient)
            self.first_state = True
        else:
            self.orientation = deepcopy(self._alt_orient)
            self.first_state = False

        self._matrix_size = len(self._init_orient)


    def rotate_cw(self):
        """Overwrites Piece.rotate_cw to just returning a new piece with the opposite orientation."""
        return self.__class__(not self.first_state)

    def rotate_ccw(self):
        """Overwrites Piece.rotate_ccw to just returning a new piece with the opposite orientation."""
        return self.__class__(not self.first_state)

class I_Piece(Piece):

    _init_orient = [
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False]
    ]
    # If I decide that this is a Two_State_Piece again:
    # _alt_orient = [
    #     [True, True, True, True],
    #     [False, False, False, False],
    #     [False, False, False, False],
    #     [False, False, False, False]
    # ]
    color = Palette.I
    _rot_for_profile = 1
class J_Piece(Piece):

    _init_orient = [
        [False, True, False],
        [False, True, False],
        [True, True, False]
    ]
    color = Palette.J
    _rot_for_profile = 1
class L_Piece(Piece):

    _init_orient = [
        [False, True, False],
        [False, True, False],
        [False, True, True]
    ]
    color = Palette.L
    _rot_for_profile = -1
class S_Piece(Two_State_Piece):

    _init_orient = [
        [False, True, True],
        [True, True, False],
        [False, False, False]
    ]
    _alt_orient = [
        [True, False, False],
        [True, True, False],
        [False, True, False]
    ]
    color = Palette.S
class Z_Piece(Two_State_Piece):

    _init_orient = [
        [True, True, False],
        [False, True, True],
        [False, False, False]
    ]
    _alt_orient = [
        [False, False, True],
        [False, True, True],
        [False, True, False]
    ]
    color = Palette.Z
class T_Piece(Piece):

    _init_orient = [
        [False, True, False],
        [True, True, True],
        [False, False, False]
    ]
    color = Palette.T
class O_Piece(Piece):

    _init_orient = [
        [False, True, True],
        [False, True, True],
        [False, False, False]
    ]
    color = Palette.O

    def rotate_cw(self):
        """Overrides Piece.rotate_cw. Returns self to avoid issues."""
        return self
    def rotate_ccw(self):
        """Overrides Piece.rotate_cw. Returns self to avoid issues."""
        return self

PIECES = (I_Piece, J_Piece, L_Piece, S_Piece, Z_Piece, T_Piece, O_Piece)


def freeze_test(game):
    """Uses console input to move control movement manually.

    Parameters
    ----------
    game : Game
        The instance of Game being played.
    """
    game.current = next(game.piece_buffer)

    print('z for quit, 2 for place, r for hold, s for down, f for hard drop, w for up, a for left, d for right, q for ccw rotate, e for cw rotate.\n')

    while True:
        inp = input(' - ')

        if 'z' in inp:
            break
        elif 'r' in inp:
            game.hold()
            game._already_held = False
        elif 'w' in inp:
            game.current_coord[0] -= 1
            game.update_cvs()
        elif 's' in inp:
            game.down()
        elif 'a' in inp:
            game.left()
        elif 'd' in inp:
            game.right()
        elif 'q' in inp:
            game.rotate_ccw()
        elif 'e' in inp:
            game.rotate_cw()
        elif 'f' in inp:
            game.hard_drop()
        elif '2' in inp:
            game.make_permanent()

if __name__ == '__main__':
    init()
    game = Game()
