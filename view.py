"""
Module: view

Classes related to the view of the natural selection simulation

View class frame heirarchy:

- View(tk.Tk)
    - BoardView(tk.Frame)
        - SquareView(tk.Frame) (# of Tile objects = board dimensions)
            - PredatorView(tk.Frame) (# of Predator objects in the tile)
            - PreyView(tk.Canvas) (# of Prey objects in the tile)
    - Title(tk.Frame)
    - LeftMenu(tk.Frame)
        - GameControls(tk.Frame)
        - Configurations(tk.Frame)
    - RightMenu(tk.Frame)
        - ScoreBoard(tk.Frame)
        - BoardKey(tk.Frame)
            - PredatorView(tk.Frame)
            - PreyView(tk.Canvas)
"""

import tkinter as tk
from tkinter import ttk
import random
from model import CurrentSettings, SquareModel, PredatorModel, PreyModel


class View(tk.Tk):
    """
    Holds the tkinter GUI for the game
    """

    settings: 'CurrentSettings'

    def __init__(self, settings: 'CurrentSettings'):
        self.settings = settings
        # setting View object up as a tkinter window
        super().__init__()
        self.title('Natural Selection Game Simulation')
        self.state('zoomed') # fullscreen including exit button and title

        # places frames/visuals
        self.title_frame = Title(self)
        self.board_frame = BoardView(self)
        self.left_menu_frame = LeftMenu(self)
        self.right_menu_frame = RightMenu(self)


class BoardView(tk.Frame):
    """
    Holds the gameboard display
    """

    parent: View
    board_data: list[list[SquareModel]] # attributed when start game button is pressed
    board_visuals_2d: list[list['SquareView']] # attributed when draw board method is called
    board_visuals_1d: list['SquareView'] # attributed when the draw board method is called
    board_visuals_diagonal_matrix: list[list['SquareView']] # attributed when the draw board method is called

    def __init__(self, parent: View):
        # setting parent frame for settings retrieval
        self.parent = parent
        board_length = self.parent.settings.board_length
        self.board_visuals_1d = []
        self.rel_tile_width_and_height = 1/board_length
        # assigning its own frame to the parent and setting its border
        super().__init__(parent, bd=3, relief='solid')
        # drawing the board (without animals)
        self.draw_board()
        # placing itself in the window
        self.place(relx=0.3, rely=0.1, relwidth=0.56, relheight=0.9)

    def draw_board(self):
        """
        Clears and redraws all Tile frames on the board
        """
        checker_color_1 = self.parent.settings.checkered_color1
        checker_color_2 = self.parent.settings.checkered_color2
        board_length = self.parent.settings.board_length
        
        # clearing board
        if self.board_visuals_1d:
            for square_view in self.board_visuals_1d:
                square_view.destroy() # removing from gui
                del square_view # removing it from memory and the list
        self.board_visuals_2d = [[] for _ in range(board_length)]

        # resetting all previous column and row weights to 0 - removes grid configuration
        i = 0
        while True:
            try:
                self.columnconfigure(i, weight=0)
                i += 1
            except:
                break
        
        i = 0
        while True:
            try:
                self.rowconfigure(i, weight=0)
                i += 1
            except:
                break

        # configuring the new grid for SquareView placement
        for i in range(board_length):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)
        
        # adding all SquareView frames to the board
        for x in range(board_length):
            for y in range(board_length):
                if (x-y) % 2 == 0:
                    color = checker_color_1
                else:
                    color = checker_color_2
                new_square_view = SquareView(self, (x, y), color)
                self.board_visuals_2d[x].append(new_square_view)
                # creating a 1d array - needed for randomly placing animals
                self.board_visuals_1d.append(new_square_view)
        
        # creating a diagonal matrix for round change visuals - board results are shown from top left to bottom right
        self.produce_diagonal_matrix()

    def randomly_draw_all_animals(self):
        """
        First erases all existing animal pieces from every square 
        then draws all new animal pieces on the board randomly
        """
        self.delay_between_pawn_placement = self.parent.settings.delay_between_random_pawn_placement
        # grabbing a list of all animal pawns
        self.all_animal_pawns: list['PredatorView | PreyView'] = [] # type: ignore
        for square_view in self.board_visuals_1d:
            for animal_pawn in square_view.square_animal_views:
                self.all_animal_pawns.append(animal_pawn)

        # randomly placing animals 1 by 1 at start of game
        self.place_pawn()
    
    def place_pawn(self):
        """
        Draws a single pawn on a square then schedules itself
        to be called again after the delay_between_pawn_placement
        """
        if self.all_animal_pawns:
            random_pawn = random.choice(self.all_animal_pawns)
            random_pawn.draw_piece()
            self.all_animal_pawns.remove(random_pawn)
            # adding delay to placement
            self.after(int(self.delay_between_pawn_placement), self.place_pawn)
    
    def diagonal_matrix_draw_all_results(self):
        """
        Draws all square winner/loser symbols from the top left of the board
        to the bottom right of the board
        Function to be called during the middle of every round to show each square's results
        """
        self.result_delay = self.parent.settings.delay_between_square_results_labels
        self.num_diagonal_sections = len(self.board_visuals_diagonal_matrix)
        # keeping track of previous symbols displayed to forget them after the delay between square results
        self.previous_square_winner_symbols = []
        # drawing the feature
        self.draw_section_results(0)

    def draw_section_results(self, index: int):
        """
        Draws the result symbols for a diagonal section of the maze
        Waits delay_between_square_results_labels until the next call of itself
        """
        if index < self.num_diagonal_sections:
            # making last diagonal section square result symbols disappear/destroy
            for previous_square_winner_symbol in self.previous_square_winner_symbols:
                previous_square_winner_symbol.destroy() # removes symbol from gui
                del previous_square_winner_symbol # removes symbol from list

            # displaying current diagonal sections square results
            for square_view in self.board_visuals_diagonal_matrix[index]:
                square_view.display_square_winner()
                self.previous_square_winner_symbols.append(square_view.square_winner_canvas)

            # adding delay to square diagonal sections being displayed
            self.after(int(self.result_delay), self.draw_section_results, index+1)
        else:
            # forgetting any square symbols left (bottom right square)
            self.previous_square_winner_symbols[0].destroy()

    def produce_diagonal_matrix(self):
        """
        Reformats board_visuals_2d array into a separate diagonal matrix
        Needed for displaying each squares results from top left of board to bottom right
        """
        # length is equal to the number of columns
        board_length = len(self.board_visuals_2d)
        num_inner_lists = board_length*2-1
        self.board_visuals_diagonal_matrix = [[] for _ in range(num_inner_lists)]
        # finding the right inner list to place square views into
        for x, column in enumerate(self.board_visuals_2d):
            for y, square_view in enumerate(column):
                self.board_visuals_diagonal_matrix[x+y].append(square_view)

    def erase_all_animals(self):
        """
        Erases all animals from every square of the board
        """
        for square_view in self.board_visuals_1d:
            square_view.erase_animals()

    def display_all_tile_results(self):
        """
        Draws either an 'X' or '+' on all board tiles from top left to bottom right
        """
    
    def display_round_countdown(self):
        """
        Draws a large number countdown center of the board
        The duration of the countdown can be customized (delay) and found in the settings
        Example countdown: 3, 2, 1, GO! (with each one fading away)
        """
    
    def display_tile_results(self):
        """
        Draws either an 'X' or '+' on its board tile
        """


class SquareView(tk.Frame):
    """
    Holds the presentation of a single board tile
    """

    parent: BoardView
    square_data: SquareModel # attributed when start game button is pressed
    square_animal_views: list['PredatorView | PreyView'] # attributed when the create_animals() method is called
    square_winner_canvas: tk.Canvas

    def __init__(self, parent: 'BoardView', position: tuple[int, int], background_color: str):
        """
        Draws a tile on the Board frame in a specified grid cell
        """
        # setting parent frame for settings retrieval
        self.parent = parent
        self.background_color = background_color
        self.square_animal_views = []
        # assigning the tile frame inside of the board frame and adding a border
        super().__init__(parent, bd=4, relief='solid', background=self.background_color)
        # board coordinates (0-board_length)
        self.x, self.y = position
        # placing itself fully in grid based off coordinates
        self.grid(column=self.x, row=self.y, sticky='nsew')

    def create_animals(self):
        """
        Creates all animal pieces on its board tile
        square_data will have been initialized to this square immediately before
        the controller's call of this function

        Square visual is a 3x3 grid: (0, 1, 2) x (0, 1, 2) coordinates
        prey and predator pawns are sorted by level and distributed in descending order:
            predators are placed from column 0 down, to the bottom of column 1 then up, etc
            prey are placed from column 2 down -
            If there are 4 prey, the highest level is placed at the top of column 1, then
            the others are distributed down column 2
            
        There is a population cap of 4 prey and 4 predators per square at the start of the round
        All animal pawns have a relative side length of 0.2
        They are spaced from each other and the square frame by a relative length of 0.1
        """
        # sorting by descending skill levels to format the animal pieces by level
        self.square_data.predators.sort(reverse=True, key=lambda prey: prey.skill_level)
        self.square_data.prey.sort(reverse=True, key=lambda predator: predator.skill_level)
        # nicknaming
        predators = self.square_data.predators
        prey = self.square_data.prey
        predator_background_color = self.parent.parent.settings.predator_background_color
        predator_outline_color = self.parent.parent.settings.predator_outline_color
        prey_background_color = self.parent.parent.settings.prey_background_color
        prey_outline_color = self.parent.parent.settings.prey_outline_color
        # drawing predators from the top left
        for i, predator in enumerate(predators):
            # finding placement and placing pawn according to pattern described in docstring
            if i <= 2:
                if i == 0:
                    relative_placement = (0.1, 0.1)
                elif i == 1:
                    relative_placement = (0.1, 0.4)
                else:
                    relative_placement = (0.1, 0.7)
            elif i <= 5:
                if i == 3:
                    relative_placement = (0.4, 0.7)
                elif i == 4:
                    relative_placement = (0.4, 0.4)
                else:
                    relative_placement = (0.4, 0.1)
            else:
                if i == 6:
                    relative_placement = (0.7, 0.1)
                elif i == 7:
                    relative_placement = (0.7, 0.4)
                else:
                    relative_placement = (0.7, 0.7)

            # creating animal to display and then adding it to the square's animal views list
            predator_to_display = PredatorView(self, relative_placement, predator, predator_background_color, predator_outline_color)
            self.square_animal_views.append(predator_to_display)
        

            # drawing predators from the top right
            # not possible for there to be more than 4 predators at the end of the round
            # finding placement and placing pawn according to pattern described in docstring
            if len(prey) < 4:
                for i, p in enumerate(prey):
                    if i == 0:
                        relative_placement = (0.7, 0.1)
                    elif i == 1:
                        relative_placement = (0.7, 0.4)
                    else:
                        relative_placement = (0.7, 0.7)

                    # creating animal to display and then adding it to the square's animal views list
                    prey_to_display = PreyView(self, relative_placement, p, self.background_color, prey_background_color, prey_outline_color)
                    self.square_animal_views.append(prey_to_display)
            else:
                # special pattern change when there are 4 prey
                for i, p in enumerate(prey):
                    if i == 0:
                        relative_placement = (0.4, 0.1)
                    elif i == 1:
                        relative_placement = (0.7, 0.1)
                    elif i == 2:
                        relative_placement = (0.7, 0.4)
                    else:
                        relative_placement = (0.7, 0.7)

                    # creating animal to display and then adding it to the square's animal views list
                    prey_to_display = PreyView(self, relative_placement, p, self.background_color, prey_background_color, prey_outline_color)
                    self.square_animal_views.append(prey_to_display)

    def draw_animals(self):
        """
        Draws all animals in its own square frame
        """
        for animal_view in self.square_animal_views:
            animal_view.draw_piece()
            animal_view.place(relx=animal_view.relative_placement[0], rely=animal_view.relative_placement[1])

    def erase_animals(self):
        """
        Removes all animal piece visuals from its respective square
        """
        for animal_pawn in self.square_animal_views:
            animal_pawn.destroy()

    def display_square_winner(self):
        """
        Displays either a predator win symbol (X), a prey win symbol
        (+), or tie symbol (-) in its respective square frame
        """
        # updates and calculates size of the frame
        self.update_idletasks()
        frame_length = self.winfo_width()
        line_symbol_padding = frame_length*0.2

        winner_int = self.square_data.winner

        # prey win
        if winner_int == 1:
            self.square_winner_canvas = tk.Canvas(self, background='green', highlightthickness=0)
            # placing lines for the symbol
            self.square_winner_canvas.create_line(line_symbol_padding, frame_length/2,
                                        frame_length-line_symbol_padding, frame_length/2, fill='dark green')
            self.square_winner_canvas.create_line(frame_length/2, line_symbol_padding, frame_length/2,
                                        frame_length-line_symbol_padding, fill='dark green')
        # predators win
        elif winner_int == -1:
            self.square_winner_canvas = tk.Canvas(self, background='red', highlightthickness=0)
            # placing lines for the symbol
            self.square_winner_canvas.create_line(line_symbol_padding, frame_length-line_symbol_padding,
                                            frame_length-line_symbol_padding, line_symbol_padding, fill='dark red')
            self.square_winner_canvas.create_line(line_symbol_padding, line_symbol_padding,
                                            frame_length-line_symbol_padding, frame_length-line_symbol_padding, fill='dark red')
        # tie
        else:
            self.square_winner_canvas = tk.Canvas(self, background='gray', highlightthickness=0)
            # placing line for symbol
            self.square_winner_canvas.create_line(line_symbol_padding, frame_length/2,
                                   frame_length-line_symbol_padding, frame_length/2, fill='dark gray')
        
        # placing the symbol
        self.square_winner_canvas.place(relwidth=1, relheight=1)


class PredatorView(tk.Frame):
    """
    Square representation for a predator game piece
    """

    parent: SquareView
    relative_placement: tuple[float, float]

    def __init__(self, parent: 'SquareView', relative_placement: tuple[float, float], data: PredatorModel,
                 background_color: str, outline_color: str):
        """
        relative_placement (tuple[float, float]):
            - (0) the relative x value within the square frame to place the piece (0-1)
            - (1) the relative y value within the square frame to place the piece (0-1)
        """
        # pulling settings
        self.parent = parent
        self.level = data.skill_level
        self.birth_round = data.birth_round
        self.relative_placement = relative_placement
        hunger_level = data.rounds_until_starvation
        if hunger_level == 1:
            self.hunger_color = parent.parent.parent.settings.one_round_until_starvation_color
        elif hunger_level == 2:
            self.hunger_color = parent.parent.parent.settings.two_rounds_until_starvation_color
        else:
            self.hunger_color = parent.parent.parent.settings.three_or_more_rounds_until_starvation_color

        # depending on settings (board dimensions), choose a certain border width
        super().__init__(parent, bd=2, relief='solid', background=self.hunger_color,
                         highlightbackground=outline_color)

    def draw_piece(self):
        # depending on board_length, choosing certain font sizes and birth round label padding
        board_length = self.parent.parent.parent.settings.board_length
        level_label_font_size = 100//(board_length*2)
        birth_label_font_size = 60//(board_length*2)
        birth_label_padding = 40//(board_length*2)

        self.level_label = ttk.Label(self, font=('Arial', level_label_font_size, 'bold'),
                                     text=self.level, background=self.hunger_color, anchor='center')
        self.birth_label = ttk.Label(self, font=('Arial', birth_label_font_size, 'bold'),
                                     text=self.birth_round, background=self.hunger_color)
        # placing labels
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.level_label.grid(row=0, column=0, sticky='se', padx=birth_label_padding, pady=birth_label_padding)
        self.birth_label.grid(row=0, column=0, sticky='nw', padx=birth_label_padding, pady=birth_label_padding)

        # placing frame and coloring it in
        self.place(relx=self.relative_placement[0], rely=self.relative_placement[1], relwidth=0.2, relheight=0.2)


class PreyView(tk.Canvas):
    """
    Circle representation for a prey game piece
    """

    parent: SquareView
    relative_placement: tuple[float, float]

    def __init__(self, parent: 'SquareView', relative_placement: tuple[float, float], data: PreyModel,
                 frame_background_color: str, circle_background_color: str, outline_color: str):
        """
        relative_placement (tuple[float, float]):
            - (0) the relative x value within the square frame to place the piece (0-1)
            - (1) the relative y value within the square frame to place the piece (0-1)
        """
        # attributing canvas in parent tile frame
        super().__init__(parent, background=frame_background_color,
                         highlightbackground=outline_color, highlightthickness=0)
        self.parent = parent
        self.level = data.skill_level
        self.birth_round = data.birth_round
        self.circle_background_color = circle_background_color
        self.outline_color = outline_color
        self.relative_placement = relative_placement

    def draw_piece(self):
        """
        Draws the prey game piece
        Outline is a circle
        Inside the middle of the circle is a level label
        On the top left edge of the circle is a birth label
        """
        # must place frame before drawing pieces for winfo_width/height to work
        self.place(relx=self.relative_placement[0], rely=self.relative_placement[1], relwidth=0.2, relheight=0.2)
        # updates and calculates size of the frame
        self.update_idletasks()
        width, height = self.winfo_width()-3, self.winfo_height()-3
        x0, y0 = 3, 3  # top left coordinates of bounding rectangle
        x1, y1 = width, height  # bottom right coordinates of bounding rectangle
        # depending on settings (board dimensions), choose a certain border width
        self.create_oval(x0, y0, x1, y1, fill=self.circle_background_color, outline=self.outline_color)
        # depending on board_length, choosing certain font sizes and birth round label padding
        board_length = self.parent.parent.parent.settings.board_length
        level_label_font_size = 100//(board_length*2)
        birth_label_font_size = 60//(board_length*2)
        birth_label_padding = 40//(board_length*2)

        self.level_label = ttk.Label(self, text=self.level, font=('Arial', level_label_font_size, 'bold'),
                                     background=self.circle_background_color, anchor='center')
        self.birth_label = ttk.Label(self, text=self.birth_round, font=('Arial', birth_label_font_size, 'bold'),
                                     background=self.circle_background_color)
        # placing labels
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1) 

        self.level_label.grid(row=0, column=0, padx=0.5, pady=0.5)
        self.birth_label.grid(row=0, column=0, sticky='w', padx=birth_label_padding, pady=birth_label_padding)


class Title(tk.Frame):
    """
    Holds the Game's title
    """

    parent: View

    def __init__(self, parent: View):
        # setting parent frame for settings retrieval
        self.parent = parent
        # assigning frame inside of its parent frame and setting border
        super().__init__(parent, bd=3, relief='solid', bg=self.parent.settings.title_background_color)
        
        # creating and placing widgets
        self.create_widgets()
        self.set_widgets()

        # placing its own frame inside parent frame
        self.place(relwidth=1, relheight=0.1)
    
    def create_widgets(self):
        """
        Creates the widgets to go inside the title
        """

        self.title_header = ttk.Label(self, text='Evolving Battles: Predators vs. Prey',
                                      font=(self.parent.settings.title_font, 45, 'bold'), 
                                      background=self.parent.settings.title_background_color,
                                      foreground=self.parent.settings.title_font_color)
    
    def set_widgets(self):
        """
        Sets the widgets inside of the title frame
        """

        self.title_header.place(relx=0.5, rely=0.5, anchor='center')


class LeftMenu(tk.Frame):
    """
    Holds the configurations and game controls frame
    """

    parent: View

    def __init__(self, parent: View):
        # setting parent frame for settings retrieval
        self.parent = parent
        # assigning the menu frame to the window and setting a border
        super().__init__(parent, bd=2, relief='solid', bg=self.parent.settings.left_menu_background_color)
        # setting up widget styles
        widget_background_color = self.parent.settings.widget_background_color
        widget_style = ttk.Style()
        widget_style.configure('TButton', background=widget_background_color, font=('Arial', 12, 'bold'))
        widget_style.configure('TScale', background=widget_background_color)
        widget_style.configure('TCombobox', fieldbackground=widget_background_color, font=('Arial', 12, 'bold'))
        # creating child frames - pack from top to bottom upon construction
        self.game_controls = GameControls(self)
        self.configurations = Configurations(self)
        # placing the menu within the window
        self.place(relx=0, rely=0.1, relwidth=0.3, relheight=0.9)


class GameControls(tk.Frame):
    """
    Holds the buttons managing the execution of the game (restart game, start round, pause, autofinish game)
    Additionally, holds the button for exporting the last completed game's data to excel
    """

    parent: LeftMenu

    def __init__(self, parent: LeftMenu):
        # setting parent frame for settings retrieval
        self.parent = parent
        self.background_color = self.parent.parent.settings.game_controls_background_color
        # assigning frame to its parent frame and setting its border
        super().__init__(parent, bd=2.5, relief='solid', bg=self.background_color)
        # filling the frame with widgets
        self.create_widgets()
        self.place_widgets()
        # puts its frame in the top of the LeftMenu frame
        self.pack(padx=20, pady=20, fill='both')
    
    def create_widgets(self):
        """
        Creates the widgets for the inside of this frame
        """
        self.title = ttk.Label(self, text='Game Controls', background=self.background_color, font=("Arial", 39, 'underline'))
        # creating game control buttons
        self.start_game_button = ttk.Button(self, text=' Start\nGame')
        self.reset_game_button = ttk.Button(self, text='Reset\nGame')
        self.autofinish_game_button = ttk.Button(self, text='Autofinish\n    Game')
        self.pause_button = ttk.Button(self, text='Pause\n Game')
        self.start_round_button = ttk.Button(self, text='  Start\nRound')
        self.export_data_button = ttk.Button(self, text='    Export\nGame Data\n   to Excel')
        # creating a scale to the user assign a certain number of rounds for the game
        self.number_of_rounds_scale_label = ttk.Label(self, text='Number of Rounds:', background=self.background_color, font=("Arial", 16, 'bold'))
        self.number_of_rounds_scale = ttk.Scale(self, from_=1, to=30, length=150)
        self.number_of_rounds_scale.set(5) # set at default
        self.number_of_rounds_scale_marker = ttk.Label(self, text='5', background=self.background_color, font=("Arial", 16, 'bold'))
    
    def place_widgets(self):
        """
        Places the widgets inside of this frame
        """
        # configuring the grid for widget placement
        self.rowconfigure((0, 1, 2, 3), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        self.title.grid(row=0, sticky='ns', columnspan=3)
        # placing game control buttons
        self.start_game_button.grid(row=1, column=0, padx=10, pady=15)
        self.reset_game_button.grid(row=1, column=0, padx=10, pady=15)
        self.reset_game_button.grid_forget()
        self.autofinish_game_button.grid(row=1, column=1, padx=10, pady=15)
        self.pause_button.grid(row=2, column=0, padx=10, pady=10)
        self.start_round_button.grid(row=2, column=1, padx=10, pady=10)
        self.export_data_button.grid(row=1, column=2, padx=15, pady=15, rowspan=2, sticky='ne')
        # placing number of rounds scale
        self.number_of_rounds_scale_label.grid(row=3, column=0, columnspan=2, padx=5, pady=10)
        self.number_of_rounds_scale.grid(row=3, column=2, sticky='e', padx=(5, 20))
        self.number_of_rounds_scale_marker.grid(row=3, column=1, sticky='e')


class Configurations(tk.Frame):
    """
    Holds all tkinter labels and widgets related to the user customizations
    """

    parent: LeftMenu
    custom_board_checkbox_value: tk.IntVar
    custom_animals_checkbox_value: tk.IntVar
    automatic_round_start_checkbox_value: tk.IntVar

    def __init__(self, parent: LeftMenu):
        # setting parent frame for settings retrieval
        self.parent = parent
        self.background_color = self.parent.parent.settings.customize_settings_background_color
        # assigning frame to its parent frame and setting its border
        super().__init__(parent, bd=2.5, relief='solid', bg=self.background_color)
        # assigning stored values for checkbuttons
        self.custom_board_checkbox_value = tk.IntVar()
        self.custom_animals_checkbox_value = tk.IntVar()
        self.automatic_round_start_checkbox_value = tk.IntVar()
        # filling frame with widgets
        self.create_widgets()
        self.place_widgets()
        # packing frame from top down - below the GameControl frame
        self.pack(padx=20, pady=0, fill='both')
    
    def create_widgets(self):
        """
        Creates the widgets for the inside of this frame
        """

        self.title = ttk.Label(self, text='Customize Settings', background=self.background_color, font=("Arial", 39, 'underline'), anchor='center')
    
        self.restore_default_settings_button = ttk.Button(self, text=' Restore\n Default\nSettings', width=10)
        # adding labels and list boxes for the Customize Board options
        self.custom_board_checkbutton = tk.Checkbutton(self, text='Customize Board', bg=self.background_color,
                                                onvalue=True, offvalue=False,
                                                font=("Arial", 18, 'bold'), activebackground=self.background_color,
                                                variable=self.custom_board_checkbox_value)
        
        self.custom_board_size_label = ttk.Label(self, text='Board Size: ', background=self.background_color, font=("Arial", 13))
        self.custom_board_size_box = ttk.Combobox(self, values=[f'{i}x{i}' for i in range(1, self.parent.parent.settings.max_board_length+1)],
                                         state='readonly', width=13)
        board_size = self.parent.parent.settings.board_length
        self.custom_board_size_box.set(f"{board_size}x{board_size}")
        
        self.custom_checker_color_label = ttk.Label(self, text='Board Colors: ', background=self.background_color, font=("Arial", 13))
        self.custom_checker_color_box = ttk.Combobox(self, values=[f'Gray x Beige', 'Gray x White', 'Beige x White', 'Pink x White'],
                                                state='readonly', width=13)
        color1 = self.parent.parent.settings.checkered_color1
        color2 = self.parent.parent.settings.checkered_color2
        self.custom_checker_color_box.set(f"{(color1).capitalize()} x {(color2).capitalize()}")

        # adding labels and scales for the Customize Starting Animals options
        self.custom_animals_checkbutton = tk.Checkbutton(self, text='Customize Starting Animals', bg=self.background_color,
                                                onvalue=True, offvalue=False,
                                                font=("Arial", 18, 'bold'), activebackground=self.background_color,
                                                variable=self.custom_animals_checkbox_value)
        # customization of starting predators
        self.custom_predator_label = ttk.Label(self, text='Predators:', background=self.background_color, font=("Arial", 16))

        max_population = (self.parent.parent.settings.board_length ** 2) * 4 # max population is 4*number of squares

        self.custom_predator_population_scale_label = ttk.Label(self, text='Population:', background=self.background_color, font=("Arial", 13))
        self.custom_predator_population_scale = ttk.Scale(self, from_=0, to=max_population, length=150)
        self.custom_predator_population_scale.set(16)
        self.predator_population_scale_marker = ttk.Label(self, text='16', background=self.background_color, font=("Arial", 14, 'bold'))

        self.custom_predator_level_scale_label = ttk.Label(self, text='Visual Acuity Level:', background=self.background_color, font=("Arial", 13))
        self.custom_predator_level_scale = ttk.Scale(self, from_=0, to=10, length=150)
        self.custom_predator_level_scale.set(5)
        self.predator_level_scale_marker = ttk.Label(self, text='5', background=self.background_color, font=("Arial", 14, 'bold'))

        self.custom_predator_starvation_scale_label = ttk.Label(self, text='Hunger:', background=self.background_color, font=("Arial", 13))
        self.custom_predator_starvation_scale = ttk.Scale(self, from_=1, to=10, length=150)
        self.custom_predator_starvation_scale.set(2)
        self.starvation_scale_marker = ttk.Label(self, text='2', background=self.background_color, font=("Arial", 14, 'bold'))

        # customization of starting prey
        self.custom_prey_label = ttk.Label(self, text='Prey:', background=self.background_color, font=("Arial", 16))

        self.custom_prey_population_scale_label = ttk.Label(self, text='Population:', background=self.background_color, font=("Arial", 13))
        self.custom_prey_population_scale = ttk.Scale(self, from_=0, to=max_population, length=150)
        self.custom_prey_population_scale.set(16)
        self.prey_population_scale_marker = ttk.Label(self, text='16', background=self.background_color, font=("Arial", 14, 'bold'))

        self.custom_prey_level_scale_label = ttk.Label(self, text='Camoflauge Level:', background=self.background_color, font=("Arial", 13))
        self.custom_prey_level_scale = ttk.Scale(self, from_=0, to=10, length=150)
        self.custom_prey_level_scale.set(5)
        self.prey_level_scale_marker = ttk.Label(self, text='5', background=self.background_color, font=("Arial", 14, 'bold'))
        
        # adding labels and scales for the Automatic Round Start options
        self.automatic_round_start_checkbutton = tk.Checkbutton(self, text='Automatic Round Start', bg=self.background_color,
                                                onvalue=True, offvalue=False,
                                                font=("Arial", 18, 'bold'), activebackground=self.background_color,
                                                variable=self.automatic_round_start_checkbox_value)

        self.round_delay_label = ttk.Label(self, text='Delay Between Rounds:', background=self.background_color, font=("Arial", 13))
        self.custom_round_delay_scale = ttk.Scale(self, from_=0, to=10, length=150)
        self.custom_round_delay_scale.set(3)
        self.custom_round_delay_scale_marker = ttk.Label(self, text='3s', background=self.background_color, font=("Arial", 14, 'bold'))
    
    def place_widgets(self):
        """
        Places the widgets inside of this frame
        """
        # configuring grid layout
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ,10, 11, 12, 13), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        self.title.grid(row=0, columnspan=3)

        # placing labels and scales for Customize Board options
        self.custom_board_checkbutton.grid(row=1, column=0, sticky='w', columnspan=2, padx=5, pady=(8, 5))

        self.restore_default_settings_button.grid(row=1, column=2, sticky='ne', padx=(0, 15), pady=(15, 0), rowspan=4)

        self.custom_board_size_label.grid(row=2, column=0, sticky='w', padx=55, columnspan=2)
        self.custom_board_size_label_grid_info = self.custom_board_size_label.grid_info()
        self.custom_board_size_label.grid_forget()

        self.custom_board_size_box.grid(row=2, column=1, sticky='e', padx=15, pady=5)
        self.custom_board_size_box_grid_info = self.custom_board_size_box.grid_info()
        self.custom_board_size_box.grid_forget()

        self.custom_checker_color_label.grid(row=3, column=0, sticky='w', padx=40, columnspan=2)
        self.custom_checker_color_label_grid_info = self.custom_checker_color_label.grid_info()
        self.custom_checker_color_label.grid_forget()

        self.custom_checker_color_box.grid(row=3, column=1, sticky='e', padx=15, pady=5)
        self.custom_checker_color_box_grid_info = self.custom_checker_color_box.grid_info()
        self.custom_checker_color_box.grid_forget()

        # placing labels and scales for the custom round delay options
        self.automatic_round_start_checkbutton.grid(row=4, sticky='w', padx=5, pady=5, columnspan=3)
        self.round_delay_label.grid(row=5, column=0, sticky='e', padx=37, columnspan=2)
        self.round_delay_label_grid_info = self.round_delay_label.grid_info()
        self.round_delay_label.grid_forget()

        self.custom_round_delay_scale.grid(row=5, column=1, sticky='e', padx=25, pady=10, columnspan=4)
        self.custom_round_delay_scale_grid_info = self.custom_round_delay_scale.grid_info()
        self.custom_round_delay_scale.grid_forget()

        self.custom_round_delay_scale_marker.grid(row=5, column=1, sticky='e')
        self.custom_round_delay_scale_marker_grid_info = self.custom_round_delay_scale_marker.grid_info()
        self.custom_round_delay_scale_marker.grid_forget()

        # placing labels and scales for Customize Starting Animals options
        self.custom_animals_checkbutton.grid(row=6, column=0, sticky='w', padx=5, pady=(5, 10), columnspan=3)
        # placing labels and scales for the custom starting predator options
        self.custom_predator_label.grid(row=7, column=0, sticky='w', padx=30, columnspan=3)
        self.custom_predator_label_grid_info = self.custom_predator_label.grid_info()
        self.custom_predator_label.grid_forget()

        self.custom_predator_population_scale_label.grid(row=8, column=0, sticky='e', padx=37, columnspan=2)
        self.custom_predator_population_scale_label_grid_info = self.custom_predator_population_scale_label.grid_info()
        self.custom_predator_population_scale_label.grid_forget()

        self.custom_predator_population_scale.grid(row=8, column=2, sticky='w', padx=10, pady=5)
        self.custom_predator_population_scale_grid_info = self.custom_predator_population_scale.grid_info()
        self.custom_predator_population_scale.grid_forget()

        self.predator_population_scale_marker.grid(row=8, column=1, sticky='e')
        self.predator_population_scale_marker_grid_info = self.predator_population_scale_marker.grid_info()
        self.predator_population_scale_marker.grid_forget()


        self.custom_predator_level_scale_label.grid(row=9, column=0, sticky='e', padx=37, columnspan=2)
        self.custom_predator_level_scale_label_grid_info = self.custom_predator_level_scale_label.grid_info()
        self.custom_predator_level_scale_label.grid_forget()

        self.custom_predator_level_scale.grid(row=9, column=2, sticky='w', padx=10, pady=5)
        self.custom_predator_level_scale_grid_info = self.custom_predator_level_scale.grid_info()
        self.custom_predator_level_scale.grid_forget()

        self.predator_level_scale_marker.grid(row=9, column=1, sticky='e')
        self.predator_level_scale_marker_grid_info = self.predator_level_scale_marker.grid_info()
        self.predator_level_scale_marker.grid_forget()

        self.custom_predator_starvation_scale_label.grid(row=10, column=0, sticky='e', padx=37, columnspan=2)
        self.custom_predator_starvation_scale_label_grid_info = self.custom_predator_starvation_scale_label.grid_info()
        self.custom_predator_starvation_scale_label.grid_forget()

        self.custom_predator_starvation_scale.grid(row=10, column=2, sticky='w', padx=10, pady=5)
        self.custom_predator_starvation_scale_grid_info = self.custom_predator_starvation_scale.grid_info()
        self.custom_predator_starvation_scale.grid_forget()

        self.starvation_scale_marker.grid(row=10, column=1, sticky='e')
        self.starvation_scale_marker_grid_info = self.starvation_scale_marker.grid_info()
        self.starvation_scale_marker.grid_forget()

        self.custom_prey_label.grid(row=11, column=0, sticky='w', padx=30, pady=(10, 0))
        self.custom_prey_label_grid_info = self.custom_prey_label.grid_info()
        self.custom_prey_label.grid_forget()

        self.custom_prey_population_scale_label.grid(row=12, column=0, sticky='e', padx=37, columnspan=2)
        self.custom_prey_population_scale_label_grid_info = self.custom_prey_population_scale_label.grid_info()
        self.custom_prey_population_scale_label.grid_forget()

        self.custom_prey_population_scale.grid(row=12, column=2, sticky='w', padx=10, pady=5)
        self.custom_prey_population_scale_grid_info = self.custom_prey_population_scale.grid_info()
        self.custom_prey_population_scale.grid_forget()

        self.prey_population_scale_marker.grid(row=12, column=1, sticky='e')
        self.prey_population_scale_marker_grid_info = self.prey_population_scale_marker.grid_info()
        self.prey_population_scale_marker.grid_forget()

        self.custom_prey_level_scale_label.grid(row=13, column=0, sticky='e', padx=37, columnspan=2)
        self.custom_prey_level_scale_label_grid_info = self.custom_prey_level_scale_label.grid_info()
        self.custom_prey_level_scale_label.grid_forget()

        self.custom_prey_level_scale.grid(row=13, column=2, sticky='w', padx=10, pady=10)
        self.custom_prey_level_scale_grid_info = self.custom_prey_level_scale.grid_info()
        self.custom_prey_level_scale.grid_forget()

        self.prey_level_scale_marker.grid(row=13, column=1, sticky='e')
        self.prey_level_scale_marker_grid_info = self.prey_level_scale_marker.grid_info()
        self.prey_level_scale_marker.grid_forget()


class RightMenu(tk.Frame):
    """
    Holds the scoreboard and board key to the right of the gameboard
    """

    parent: View

    def __init__(self, parent: View):
        # setting parent frame for settings retrieval
        self.parent = parent
        self.background_color = self.parent.settings.right_menu_background_color
        # assigning the rightmenu frame to be within the window and setting border
        super().__init__(parent, bd=2.5, relief='solid', background=self.background_color)
        # creating child frames - packed upon construction
        self.scoreboard = ScoreBoard(self)
        self.boardkey = BoardKey(self)
        # placing the rightmenu frame within the window
        self.place(relx=0.86, rely=0.1, relwidth=0.14, relheight=0.9)


class ScoreBoard(tk.Frame):
    """
    Holds the scoreboard for the game which includes for each animal:
        - their population
        - their average level
    Additionally, holds the current round below the populations/level stats
    """

    parent: RightMenu

    def __init__(self, parent: RightMenu):
        # setting parent frame for settings retrieval
        self.parent = parent
        self.background_color = self.parent.parent.settings.scoreboard_background_color
        # assigning the scoreboard frame to be within the rightmenu and setting border
        super().__init__(parent, bd=2.5, relief='solid', background=self.background_color)

        # creating and placing widgets within the scoreboard
        self.create_widgets()
        self.place_widgets()
        # placing the scoreboard in the rightmenu from the top down
        self.pack(padx=10, pady=10, fill='both')
    
    def create_widgets(self):
        """
        Creates the widgets for the inside of this frame
        """

        self.round_label = ttk.Label(self, text='Round 1', font=("Arial", 32, "underline"),
                                     background=self.background_color, anchor='center')

        self.predator_stats_label = ttk.Label(self, text='Predator Stats:', font=("Arial", 16, "bold"),
                                              background=self.background_color)
        
        self.predator_population_label = ttk.Label(self, text='Population:', font=("Arial", 14),
                                                   background=self.background_color)
        self.predator_population_marker = ttk.Label(self, text='16', font=("Arial", 16, "bold"),
                                                    background=self.background_color)

        self.predator_level_label = ttk.Label(self, text='Avg. Level:', font=("Arial", 14),
                                              background=self.background_color)
        self.predator_level_marker = ttk.Label(self, text='5', font=("Arial", 16, "bold"),
                                               background=self.background_color)

        self.predator_starvation_label = ttk.Label(self, text="Avg. Hunger:", font=("Arial", 14),
                                                   background=self.background_color)
        self.predator_starvation_marker = ttk.Label(self, text='2', font=("Arial", 16, "bold"),
                                                    background=self.background_color)


        self.prey_stats_label = ttk.Label(self, text='Prey Stats:', font=("Arial", 15, "bold"),
                                              background=self.background_color)
        
        self.prey_population_label = ttk.Label(self, text='Population:', font=("Arial", 14),
                                                   background=self.background_color)
        self.prey_population_marker = ttk.Label(self, text='16', font=("Arial", 16, "bold"),
                                                    background=self.background_color)

        self.prey_level_label = ttk.Label(self, text='Avg. Level:', font=("Arial", 14),
                                              background=self.background_color)
        self.prey_level_marker = ttk.Label(self, text='5', font=("Arial", 16, "bold"),
                                               background=self.background_color)
        
    def place_widgets(self):
        """
        Places the widgets inside of this frame
        """
        # setting the grid
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        # setting widgets
        self.round_label.grid(column=0, row=0, columnspan=2, padx=5, pady=10)

        self.predator_stats_label.grid(column=0, row=1, padx=12, pady=5, sticky='w', columnspan=2)

        self.predator_population_label.grid(column=0, row=2, padx=50, pady=5, sticky='w', columnspan=3)
        self.predator_population_marker.grid(column=1, row=2, padx=12, pady=5, sticky='e')

        self.predator_level_label.grid(column=0, row=3, padx=50, pady=5, sticky='w', columnspan=3)
        self.predator_level_marker.grid(column=1, row=3, padx=12, pady=5, sticky='e')

        self.predator_starvation_label.grid(column=0, row=4, padx=36, pady=5, sticky='w', columnspan=3)
        self.predator_starvation_marker.grid(column=1, row=4, padx=12, pady=5, sticky='e')

        self.prey_stats_label.grid(column=0, row=5, padx=12, pady=(18, 5), sticky='w', columnspan=2)

        self.prey_population_label.grid(column=0, row=6, padx=50, pady=5, sticky='w', columnspan=3)
        self.prey_population_marker.grid(column=1, row=6, padx=12, pady=5, sticky='e')

        self.prey_level_label.grid(column=0, row=7, padx=50, pady=5, sticky='w', columnspan=3)
        self.prey_level_marker.grid(column=1, row=7, padx=12, pady=5, sticky='e')


class BoardKey(tk.Frame):
    """
    Holds the gameboard key for the predator and prey pieces
    """

    parent: RightMenu

    def __init__(self, parent: RightMenu):
        # setting parent frame for settings retrieval
        self.parent = parent
        self.background_color = self.parent.parent.settings.boardkey_background_color
        # assigning the board key frame to be within the right menu and setting border
        super().__init__(parent, bd=2, relief='solid', background=self.background_color)

        # creating and placing widgets within the boardkey frame
        self.create_widgets()
        self.place_widgets()
        # placing the boardkey below the scoreboard
        self.pack(padx=10, pady=10, fill='both')
    
    def create_widgets(self):
        """
        Creates the widgets for the inside of this frame
        """
        self.boardkey_label = ttk.Label(self, text='Board Key', font=("Arial", 29, "underline"),
                                     background=self.background_color, anchor='center')
        
        self.predator_pawn_label = ttk.Label(self, text='Predator Pawn:', font=("Arial", 16, "bold"),
                                             background=self.background_color)
        
        self.predator_level_description = ttk.Label(self, text='6: Visual Acuity Level')
        self.predator_birth_round_description = ttk.Label(self, text='1: Birth Round')
        self.predator_color_description = ttk.Label(self, text='Color: Hunger Level')
        

        self.prey_pawn_label = ttk.Label(self, text='Prey Pawn:', font=("Arial", 16, "bold"),
                                             background=self.background_color)
        
    
    def place_widgets(self):
        """
        Places the widgets inside of this frame
        """
        # setting the grid
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        # setting widgets
        self.boardkey_label.grid(column=0, row=0, columnspan=2, padx=5, pady=10)

        self.predator_pawn_label.grid(column=0, row=1, columnspan=2, padx=12, sticky='w')



        self.prey_pawn_label.grid(column=0, row=2, columnspan=2, padx=12, sticky='w')