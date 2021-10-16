#A recreation of the classic game of Tetris in Python.
Fully functional, this program allows users to play tetris in a simple graphical user interface built with Python's ```tkinter``` module. Like all tetris games, you can move, rotate, hold, and drop pieces with simple controls. These controls are all processed in tkinter's event loop with a secondary thread being run in the background to continously lower tetris pieces at increasing speeds. Players place blocks and clear lines until, eventually, they can't catch up. Each line cleared adds to their score that is displayed throughout and at the end, when the program asks if the user wants to play again. 

Some of the techniques used in this project:
* GUI Design
* Threading
* Image Manipulation
* Object-Oriented Programming
* Inheritance
* JSON

This project was in independent project created during the Fall semester of my Freshman year at Missouri S&T. It was concieved and developed within 2 weeks.

**Requirements:**
Python == 3.9.1
Pillow == 8.3.2

There are two versions of this program. The first is the 'Simple' version, which includes all developments up to the introduction of gridlines in the background of the gamefield. The second version contains these background gridlines, textures on each piece block, and eventually a high score tracking system.
