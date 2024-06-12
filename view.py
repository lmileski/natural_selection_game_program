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

import webbrowser
import os
import tkinter as tk
from tkinter import ttk
import random
from model import CurrentSettings, SquareModel, PredatorModel, PreyModel
from model_helpers import open_file


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
    animal_pawns_to_erase: list['PredatorView | PreyView']

    def __init__(self, parent: View):
        # setting parent frame for settings retrieval
        self.parent = parent
        self.board_visuals_1d = []
        self.animal_pawns_to_erase = []
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

        self.board_visuals_1d = []
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
                if (x-y) % 2 == 1:
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
        Draws or erases all new animal pieces on the board randomly
        """
        # finding the delay between each pawns placement
        random_pawn_placement_time = self.parent.settings.random_pawn_placement_time
        total_population = self.parent.settings.num_initial_predators + self.parent.settings.num_initial_prey
        self.delay_between_pawns = random_pawn_placement_time//total_population
        # grabbing a list of all animal pawns
        self.all_animal_pawns_to_change: list['PredatorView | PreyView'] = [] # type: ignore
        for square_view in self.board_visuals_1d:
            for animal_pawn in square_view.square_animal_views:
                self.all_animal_pawns_to_change.append(animal_pawn)

        # randomly drawing all animals 1 by 1 at start of game
        self.place_pawn()
    
    def randomly_collect_all_animals(self):
        """
        Erases all animal pieces on the board randomly
        """
        if self.animal_pawns_to_erase:
            random_pawn = random.choice(self.animal_pawns_to_erase)
            random_pawn.destroy()
            self.animal_pawns_to_erase.remove(random_pawn)
            # adding delay to placement
            self.after(self.delay_between_pawns, self.randomly_collect_all_animals)

    def place_pawn(self):
        """
        Draws a single pawn on a square then schedules itself
        to be called again after the delay_between_pawn_placement
        """
        if self.all_animal_pawns_to_change:
            random_pawn = random.choice(self.all_animal_pawns_to_change)
            random_pawn.draw_piece()
            self.all_animal_pawns_to_change.remove(random_pawn)
            # adding delay to placement
            self.after(self.delay_between_pawns, self.place_pawn)
    
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
        # drawing
        self.draw_section_results()

    def draw_section_results(self, index: int = 0):
        """
        Draws the result symbols for a diagonal section of the maze
        (Draws either an 'X' or '+' on all board tiles from top left to bottom right)
        Waits delay_between_square_results_labels until the next call of itself
        """
        if index < self.num_diagonal_sections:
            # making last diagonal section square result symbols disappear/destroy
            for previous_square_winner_symbol in self.previous_square_winner_symbols:
                previous_square_winner_symbol.destroy() # removes symbol from gui
                
            # displaying current diagonal sections square results and new animals
            for square_view in self.board_visuals_diagonal_matrix[index]:
                # (model has been updated by controller at this point)
                # erasing old animals
                square_view.erase_animals()
                # creating new animal views
                square_view.create_animals()
                # drawing the new animal views
                square_view.draw_animals()
                # drawing result label
                square_view.display_square_winner()
                self.previous_square_winner_symbols.append(square_view.square_winner_canvas)

            # adding delay to square diagonal sections being displayed
            self.after(self.result_delay, self.draw_section_results, index+1)
        else:
            # forgetting any square symbols left (bottom right square)
            board_length = self.parent.settings.board_length
            last_square_i = board_length ** 2 - 1
            self.previous_square_winner_symbols[last_square_i].destroy()

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
        
    def display_game_countdown(self, num_to_display: int):
        """
        Draws a large number countdown center of the board
        Example countdown: 3, 2, 1, GO!
        To be called several times with the num_to_display being the current countdown label's int

        Must create labels in same function to ensure proper level order of frames :(

        Transparent label backgrounds unfortunately don't exist in tkinter :(
        """
        board_length = self.parent.settings.board_length
        background_color = self.parent.settings.countdown_background_color
        delay_of_number = (self.parent.settings.delay_between_board_labels*2)//3
        delay_of_go = int(self.parent.settings.delay_between_board_labels*1.5)

        # forgetting the last countdown number displayed in last call if it exists (10 is max)
        last_countdown_label: tk.Label | None = getattr(self, f'countdown_label_{num_to_display+1}', None)
        if last_countdown_label:
            last_countdown_label.grid_forget()

        # for all numbers from round_delay -> 1
        if num_to_display > 0:
            # creating number label
            new_label = ttk.Label(self, text=num_to_display, background=background_color, font=("Arial", 75, 'bold'), anchor='center')
            setattr(self, f'countdown_label_{num_to_display}', new_label)
            # displaying next countdown number
            self.countdown_label: tk.Label = getattr(self, f'countdown_label_{num_to_display}')
            self.countdown_label.grid(column=0, row=0, columnspan=board_length, rowspan=board_length, sticky='nsew')
            # displaying the next countdown number after a half-second delay
            self.after(delay_of_number, self.display_game_countdown, num_to_display-1)

        # for displaying GO!
        else:
            # creating label
            self.countdown_label_go = ttk.Label(self, text='GO!', background=background_color,
                                            font=("Arial", 75, 'bold'), anchor='center')
            self.countdown_label_go.grid(column=0, row=0,
                                         columnspan=board_length, rowspan=board_length, sticky='nsew')
            # adding delay then hiding go label
            self.after(delay_of_go, lambda: self.countdown_label_go.grid_forget())

    def display_round_label(self, round_num: int):
        """
        Displays the round number in the center of the board

        Must create labels in same function to ensure proper level order of frames
        """
        board_length = self.parent.settings.board_length
        delay = self.parent.settings.delay_between_board_labels
        background_color = self.parent.settings.countdown_background_color
        # placing labels at specific time intervals
        # creating label
        self.round_label = ttk.Label(self, text='Round 1', background=background_color,
                                    font=("Arial", 60, 'bold'), anchor='center')
        # placing round label
        self.round_label.configure(text=f'Round {round_num}')
        self.round_label.grid(column=0, row=0,
                                columnspan=board_length, rowspan=board_length, sticky='nsew')
        # adding delay
        self.after(delay, lambda: self.round_label.grid_forget())       
    
    def display_scattering_pawns_label(self):
        """
        Displays the scattering pawns label

        Must create labels in same function to ensure proper level order of frames
        """
        board_length = self.parent.settings.board_length
        delay = self.parent.settings.delay_between_board_labels
        background_color = self.parent.settings.countdown_background_color
        # creating label
        self.scattering_pawns_label = ttk.Label(self, text='Scattering\n   Pawns', background=background_color,
                                            font=("Arial", 50, 'bold'), anchor='center')
        # forgetting round label
        self.round_label.grid_forget()
        # adding Scattering Pawns label
        self.scattering_pawns_label.grid(column=0, row=0,
                                        columnspan=board_length, rowspan=board_length, sticky='nsew')
        # adding delay then forgetting the GO! label
        self.after(delay, lambda: self.scattering_pawns_label.grid_forget())

    def display_winner_label(self, winner: str):
        """
        Displays the winner of the round in the center of the board
        After winner is displayed, the collecting pawns label is displayed

        Parameters:
            - winner (str): the winner of the game - either
                - 'predator' or
                - 'prey' or
                - 'tie'
        
        Must create labels in same function to ensure proper level order of frames
        """
        board_length = self.parent.settings.board_length
        delay = int(self.parent.settings.delay_between_board_labels * 2)
        background_color = self.parent.settings.countdown_background_color

        if winner == 'predator':
            self.predator_label = ttk.Label(self, text='Predators\n    Win!', background=background_color,
                                        font=("Arial", 50, 'bold'), anchor='center')
            self.predator_label.grid(column=0, row=0,
                                        columnspan=board_length, rowspan=board_length, sticky='nsew')
        elif winner == 'prey':
            self.prey_label = ttk.Label(self, text="Prey\nWin!", background=background_color,
                                    font=("Arial", 50, 'bold'), anchor='center')
            self.prey_label.grid(column=0, row=0,
                                    columnspan=board_length, rowspan=board_length, sticky='nsew')
        elif winner == 'tie':
            self.tie_label = ttk.Label(self, text="Tie!", background=background_color,
                                font=("Arial", 50, 'bold'), anchor='center')
            self.tie_label.grid(column=0, row=0,
                                columnspan=board_length, rowspan=board_length, sticky='nsew')
        else:
                raise ValueError("winner argument may only be 'predators', 'prey', or 'tie'")
        
        label_displayed = getattr(self, f'{winner}_label')
        self.after(delay, lambda: label_displayed.grid_forget())

    def display_collecting_pawns_label(self):
        """
        Displays the collecting pawns label in the board frame
        """
        board_length = self.parent.settings.board_length
        delay = self.parent.settings.delay_between_board_labels
        background_color = self.parent.settings.countdown_background_color

        self.collecting_pawns_label = ttk.Label(self, text='Collecting\n   Pawns', background=background_color,
                                                font=("Arial", 50, 'bold'), anchor='center')
        self.collecting_pawns_label.grid(column=0, row=0,
                                            columnspan=board_length, rowspan=board_length, sticky='nsew')
        self.after(delay, lambda: self.collecting_pawns_label.grid_forget())
        

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
        All animal pawns have a relative side length of 0.25
        They are spaced from the parent frame's border by a length of 0.05
        They are spaced from each other by a length of 0.075
        """
        # sorting by descending skill levels to format the animal pieces by level
        self.square_data.predators.sort(reverse=True, key=lambda prey: prey.skill_level)
        self.square_data.prey.sort(reverse=True, key=lambda predator: predator.skill_level)
        self.square_animal_views = []
        # nicknaming
        predators = self.square_data.predators
        prey = self.square_data.prey
        predator_outline_color = self.parent.parent.settings.predator_outline_color
        prey_background_color = self.parent.parent.settings.prey_background_color
        prey_outline_color = self.parent.parent.settings.prey_outline_color
        # drawing predators from the top left
        for i, predator in enumerate(predators):
            # finding placement and placing pawn according to pattern described in docstring
            if i <= 2:
                if i == 0:
                    relative_placement = (0.05, 0.05)
                elif i == 1:
                    relative_placement = (0.05, 0.375)
                else:
                    relative_placement = (0.05, 0.7)
            elif i <= 5:
                if i == 3:
                    relative_placement = (0.375, 0.7)
                elif i == 4:
                    relative_placement = (0.375, 0.375)
                else:
                    relative_placement = (0.375, 0.05)
            else:
                if i == 6:
                    relative_placement = (0.7, 0.05)
                elif i == 7:
                    relative_placement = (0.7, 0.375)
                else:
                    relative_placement = (0.7, 0.7)

            # creating animal to display and then adding it to the square's animal views list
            predator_to_display = PredatorView(self, relative_placement, predator, predator_outline_color)
            self.square_animal_views.append(predator_to_display)
        

        # drawing predators from the top right
        # not possible for there to be more than 4 predators at the end of the round
        # finding placement and placing pawn according to pattern described in docstring
        if len(prey) < 4:
            for i, p in enumerate(prey):
                if i == 0:
                    relative_placement = (0.7, 0.05)
                elif i == 1:
                    relative_placement = (0.7, 0.375)
                else:
                    relative_placement = (0.7, 0.7)

                # creating animal to display and then adding it to the square's animal views list
                prey_to_display = PreyView(self, relative_placement, p, self.background_color, prey_background_color, prey_outline_color)
                self.square_animal_views.append(prey_to_display)
        else:
            # special pattern change when there are 4 prey
            for i, p in enumerate(prey):
                if i == 0:
                    relative_placement = (0.375, 0.05)
                elif i == 1:
                    relative_placement = (0.7, 0.05)
                elif i == 2:
                    relative_placement = (0.7, 0.375)
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
            self.parent.animal_pawns_to_erase.append(animal_view)
            animal_view.draw_piece()
            animal_view.place(relx=animal_view.relative_placement[0], rely=animal_view.relative_placement[1])

    def erase_animals(self):
        """
        Removes all animal piece visuals from its respective square
        """
        for animal_pawn in self.square_animal_views:
            animal_pawn.destroy() # clears from square
        self.square_animal_views = []

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
                                        frame_length-line_symbol_padding, frame_length/2, fill='#003300',
                                        width=10)
            self.square_winner_canvas.create_line(frame_length/2, line_symbol_padding, frame_length/2,
                                        frame_length-line_symbol_padding, fill='#003300',
                                        width=10)
        # predators win
        elif winner_int == -1:
            self.square_winner_canvas = tk.Canvas(self, background='red', highlightthickness=0)
            # placing lines for the symbol
            self.square_winner_canvas.create_line(line_symbol_padding, frame_length-line_symbol_padding,
                                            frame_length-line_symbol_padding, line_symbol_padding, fill='#800000',
                                            width=10)
            self.square_winner_canvas.create_line(line_symbol_padding, line_symbol_padding,
                                            frame_length-line_symbol_padding, frame_length-line_symbol_padding, fill='#800000',
                                            width=10)
        # tie
        else:
            self.square_winner_canvas = tk.Canvas(self, background='gray', highlightthickness=0)
            # placing line for symbol
            self.square_winner_canvas.create_line(line_symbol_padding, frame_length/2,
                                   frame_length-line_symbol_padding, frame_length/2, fill='gray22',
                                   width=10)
        
        # placing the symbol
        self.square_winner_canvas.place(relwidth=1, relheight=1)


class PredatorView(tk.Frame):
    """
    Square representation for a predator game piece
    """

    parent: SquareView
    relative_placement: tuple[float, float]

    def __init__(self, parent: 'SquareView', relative_placement: tuple[float, float], data: PredatorModel, outline_color: str):
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
        
        board_length = self.parent.parent.parent.settings.board_length
        if board_length < 3:
            border_thickness = 4
        elif board_length < 6:
            border_thickness = 3
        else:
            border_thickness = 2

        # depending on settings (board dimensions), choose a certain border width
        super().__init__(parent, bd=0, relief='solid', background=self.hunger_color,
                         highlightbackground=outline_color, highlightthickness=border_thickness)

    def draw_piece(self):
        # depending on board_length, choosing certain font sizes and birth round label padding
        board_length = self.parent.parent.parent.settings.board_length

        if board_length > 4:
            level_label_font_size = 40//board_length
            birth_label_font_size = 30//board_length

        else:
            level_label_font_size = 55//board_length
            birth_label_font_size = 38//board_length

        level_label_padx = (0, 37//board_length)
        level_label_pady = (0, 20//board_length)

        birth_label_padx = (30//board_length, 0)
        birth_label_pady = (20//board_length, 0)

        self.level_label = ttk.Label(self, font=('Arial', level_label_font_size, 'bold'),
                                     text=self.level, background=self.hunger_color, anchor='center')
        self.birth_label = ttk.Label(self, font=('Arial', birth_label_font_size, 'bold'),
                                     text=self.birth_round, background=self.hunger_color)
        # placing labels
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.level_label.grid(row=0, column=0, sticky='se', padx=level_label_padx, pady=level_label_pady)
        self.birth_label.grid(row=0, column=0, sticky='nw', padx=birth_label_padx, pady=birth_label_pady)

        # placing frame and coloring it in
        self.place(relx=self.relative_placement[0], rely=self.relative_placement[1], relwidth=0.25, relheight=0.25)


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
        self.place(relx=self.relative_placement[0], rely=self.relative_placement[1], relwidth=0.25, relheight=0.25)
        # updates and calculates size of the frame
        self.update_idletasks()
        width, height = self.winfo_width()-3, self.winfo_height()-3
        x0, y0 = 3, 3  # top left coordinates of bounding rectangle
        x1, y1 = width, height  # bottom right coordinates of bounding rectangle

        board_length = self.parent.parent.parent.settings.board_length
        if board_length < 3:
            border_thickness = 4
        elif board_length < 6:
            border_thickness = 3
        else:
            border_thickness = 2

        # depending on settings (board dimensions), choose a certain border width
        self.create_oval(x0, y0, x1, y1, fill=self.circle_background_color, outline=self.outline_color, width=border_thickness)
        # depending on board_length, choosing certain font sizes and birth round label padding
        board_length = self.parent.parent.parent.settings.board_length

        if board_length > 4:
            level_label_font_size = 40//board_length
            birth_label_font_size = 30//board_length

            level_label_padx = (0, 55//board_length)
            level_label_pady = (0, 40//board_length)

            birth_label_padx = (57//board_length, 0)
            birth_label_pady = (51//board_length, 0)
        else:
            level_label_font_size = 55//board_length
            birth_label_font_size = 38//board_length

            level_label_padx = (0, 58//board_length)
            level_label_pady = (0, 38//board_length)

            birth_label_padx = (58//board_length, 0)
            birth_label_pady = (48//board_length, 0)

        self.level_label = ttk.Label(self, text=self.level, font=('Arial', level_label_font_size, 'bold'),
                                     background=self.circle_background_color)
        self.birth_label = ttk.Label(self, text=self.birth_round, font=('Arial', birth_label_font_size, 'bold'),
                                     background=self.circle_background_color)
        # placing labels
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.level_label.grid(row=0, column=0, sticky='se', padx=level_label_padx, pady=level_label_pady)
        self.birth_label.grid(row=0, column=0, sticky='nw', padx=birth_label_padx, pady=birth_label_pady)


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
        
        # adding credits/hyperlinks to title row corners
        self.program_credit = ttk.Label(self, text='Program by Luke Mileski',
                                        font=(self.parent.settings.title_font, 13, 'bold'),
                                        background=self.parent.settings.title_background_color)
        
        self.game_idea_credit = ttk.Label(self, text="Lab Game Idea by\nUSD's Dr. Searcy",
                                        font=(self.parent.settings.title_font, 13, 'bold'),
                                        background=self.parent.settings.title_background_color)
        
        self.link_to_github = ttk.Label(self, text="View my Github",
                                        font=(self.parent.settings.title_font, 13, 'bold'),
                                        background=self.parent.settings.title_background_color,
                                        cursor='hand2', foreground='dodgerblue3')
        self.link_to_github.bind("<Button-1>", lambda e: webbrowser.open( # making link label an actual link
            'https://github.com/lmileski/natural_selection_board_game'))
        
        # adding link to online game details document
        self.link_to_game_details = ttk.Label(self, text='View Lab Game Details',
                                        font=(self.parent.settings.title_font, 13, 'bold'),
                                        background=self.parent.settings.title_background_color,
                                        cursor='hand2', foreground='dodgerblue3')
        self.link_to_game_details.bind("<Button-1>", lambda e: webbrowser.open(
            'https://d.docs.live.net/3d8c06f048f6c577/Natural%20Selection%20Lab%20Automation.docx'))

    def set_widgets(self):
        """
        Sets the widgets inside of the title frame
        """

        self.title_header.place(relx=0.5, rely=0.5, anchor='center')

        self.program_credit.place(relx=0.004, rely=0.02)
        self.game_idea_credit.place(relx=0.004, rely=0.45)

        self.link_to_github.place(relx=0.917, rely=0.02)
        self.link_to_game_details.place(relx=0.88, rely=0.65)


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
        highlighted_button_style = ttk.Style()
        highlighted_button_style.configure('highlighted_button.TButton', foregr='gold', font=('Arial', 12, 'bold'))
        # creating child frames - pack from top to bottom upon construction
        self.game_controls = GameControls(self)
        self.configurations = Configurations(self)

        # creating an advisory label the default starting animals when user chooses a 1x1 board size
        self.board_size_advisory_label = ttk.Label(self, text="Default starting animal pop. exceeds a 1x1 board's pop. capacity",
                                                   font=("Arial", 11), foreground='darkorange3',
                                                   background= self.parent.settings.left_menu_background_color)
        self.board_size_advisory_label.pack(pady=3)
        self.board_size_advisory_label_pack_info = self.board_size_advisory_label.pack_info()
        self.board_size_advisory_label.pack_forget()

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
        self.start_round_button = ttk.Button(self, text='  Start\nRound', style='highlighted_button.TButton')
        self.finish_round_button = ttk.Button(self, text=' Finish\nRound', style='highlighted_button.TButton')
        self.export_data_button = ttk.Button(self, text='    Export\nGame Data\n   to Excel')
        # placeholder label for preventing game controls frame from rescaling when hiding buttons
        self.placeholder_label = ttk.Label(self, text='', background=self.background_color)
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
        self.reset_game_button.grid(row=1, column=0, padx=(30, 10), pady=15)
        self.autofinish_game_button.grid(row=2, column=0, padx=(30, 10), pady=(5, 10))
        self.pause_button.grid(row=1, column=1, padx=10, pady=15)
        self.start_round_button.grid(row=2, column=1, padx=10, pady=(5, 10))
        self.finish_round_button.grid(row=2, column=1, padx=10, pady=(5, 10))
        self.export_data_button.grid(row=1, column=2, padx=15, pady=15, rowspan=2, sticky='ne')
        # placeholder label
        self.placeholder_label.grid(row=2, column=1, padx=10, pady=(5, 40))
        # placing number of rounds scale
        self.number_of_rounds_scale_label.grid(row=3, column=0, sticky='w', columnspan=3, padx=(27, 0), pady=10)
        self.number_of_rounds_scale.grid(row=3, column=2, sticky='e', padx=(0, 25))
        self.number_of_rounds_scale_marker.grid(row=3, column=0, columnspan=3, sticky='e', padx=(0, 185))
        # remembering the grid placement of buttons to show/hide them when user starts/ends game
        self.start_game_button_grid_info = self.start_game_button.grid_info()
        self.reset_game_button_grid_info = self.reset_game_button.grid_info()
        self.autofinish_game_button_grid_info = self.autofinish_game_button.grid_info()
        self.pause_button_grid_info = self.pause_button.grid_info()
        self.start_round_button_grid_info = self.start_round_button.grid_info()
        self.finish_round_button_grid_info = self.finish_round_button.grid_info()
        self.export_data_button_grid_info = self.export_data_button.grid_info()
        self.placeholder_label_grid_info = self.placeholder_label.grid_info()
        # grid forgetting any buttons that won't be initially displayed
        self.reset_game_button.grid_forget()
        self.autofinish_game_button.grid_forget()
        self.pause_button.grid_forget()
        self.start_round_button.grid_forget()
        self.finish_round_button.grid_forget()
        self.export_data_button.grid_forget()


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
        self.custom_checker_color_box = ttk.Combobox(self, values=[f'Brown x White', 'Gray x White', 'Blue x White', 'Pink x White', 'Blue x Pink'],
                                                state='readonly', width=13)
        color1 = self.parent.parent.settings.checkered_color1
        color2 = self.parent.parent.settings.checkered_color2
        if color1 == 'navajowhite4':
            color1 = 'brown'
        if color2 == 'mint cream':
            color2 = 'white'
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

        self.custom_predator_starvation_scale_label = ttk.Label(self, text='Satiety Level:', background=self.background_color, font=("Arial", 13))
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

        default_delay = int(self.parent.parent.settings.delay_between_rounds)
        self.round_delay_label = ttk.Label(self, text='Delay Between Rounds:', background=self.background_color, font=("Arial", 13))
        self.custom_round_delay_scale = ttk.Scale(self, from_=0, to=10, length=150)
        self.custom_round_delay_scale.set(default_delay)
        self.custom_round_delay_scale_marker = ttk.Label(self, text=f'{default_delay}s', background=self.background_color, font=("Arial", 14, 'bold'))
    
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

        self.restore_default_settings_button.grid(row=1, column=2, sticky='ne', padx=(0, 25), pady=(15, 0), rowspan=4)

        self.custom_board_size_label.grid(row=2, column=0, sticky='w', padx=55, columnspan=2)
        self.custom_board_size_label_grid_info = self.custom_board_size_label.grid_info()
        self.custom_board_size_label.grid_forget()

        self.custom_board_size_box.grid(row=2, column=0, sticky='w', padx=(150, 0), pady=5, columnspan=3)
        self.custom_board_size_box_grid_info = self.custom_board_size_box.grid_info()
        self.custom_board_size_box.grid_forget()

        self.custom_checker_color_label.grid(row=3, column=0, sticky='w', padx=40, columnspan=2)
        self.custom_checker_color_label_grid_info = self.custom_checker_color_label.grid_info()
        self.custom_checker_color_label.grid_forget()

        self.custom_checker_color_box.grid(row=3, column=0, sticky='w', padx=(150, 0), pady=5, columnspan=3)
        self.custom_checker_color_box_grid_info = self.custom_checker_color_box.grid_info()
        self.custom_checker_color_box.grid_forget()

        # placing labels and scales for the custom round delay options
        self.automatic_round_start_checkbutton.grid(row=4, sticky='w', padx=5, pady=5, columnspan=3)
        self.round_delay_label.grid(row=5, column=0, sticky='w', padx=45, columnspan=3)
        self.round_delay_label_grid_info = self.round_delay_label.grid_info()
        self.round_delay_label.grid_forget()

        self.custom_round_delay_scale.grid(row=5, column=1, sticky='e', padx=25, pady=10, columnspan=3)
        self.custom_round_delay_scale_grid_info = self.custom_round_delay_scale.grid_info()
        self.custom_round_delay_scale.grid_forget()

        self.custom_round_delay_scale_marker.grid(row=5, column=0, sticky='e', columnspan=3, padx=(0, 185))
        self.custom_round_delay_scale_marker_grid_info = self.custom_round_delay_scale_marker.grid_info()
        self.custom_round_delay_scale_marker.grid_forget()

        # placing labels and scales for Customize Starting Animals options
        self.custom_animals_checkbutton.grid(row=6, column=0, sticky='w', padx=5, pady=(5, 10), columnspan=3)
        # placing labels and scales for the custom starting predator options
        self.custom_predator_label.grid(row=7, column=0, sticky='w', padx=30, columnspan=3)
        self.custom_predator_label_grid_info = self.custom_predator_label.grid_info()
        self.custom_predator_label.grid_forget()

        self.custom_predator_population_scale_label.grid(row=8, column=0, sticky='e', padx=34, columnspan=2)
        self.custom_predator_population_scale_label_grid_info = self.custom_predator_population_scale_label.grid_info()
        self.custom_predator_population_scale_label.grid_forget()

        self.custom_predator_population_scale.grid(row=8, column=1, sticky='e', padx=25, pady=5, columnspan=3)
        self.custom_predator_population_scale_grid_info = self.custom_predator_population_scale.grid_info()
        self.custom_predator_population_scale.grid_forget()

        self.predator_population_scale_marker.grid(row=8, column=0, sticky='e', columnspan=3, padx=(0, 185))
        self.predator_population_scale_marker_grid_info = self.predator_population_scale_marker.grid_info()
        self.predator_population_scale_marker.grid_forget()


        self.custom_predator_level_scale_label.grid(row=9, column=0, sticky='e', padx=34, columnspan=2)
        self.custom_predator_level_scale_label_grid_info = self.custom_predator_level_scale_label.grid_info()
        self.custom_predator_level_scale_label.grid_forget()

        self.custom_predator_level_scale.grid(row=9, column=1, sticky='e', padx=25, pady=5, columnspan=3)
        self.custom_predator_level_scale_grid_info = self.custom_predator_level_scale.grid_info()
        self.custom_predator_level_scale.grid_forget()

        self.predator_level_scale_marker.grid(row=9, column=0, sticky='e', columnspan=3, padx=(0, 185))
        self.predator_level_scale_marker_grid_info = self.predator_level_scale_marker.grid_info()
        self.predator_level_scale_marker.grid_forget()

        self.custom_predator_starvation_scale_label.grid(row=10, column=0, sticky='e', padx=34, columnspan=2)
        self.custom_predator_starvation_scale_label_grid_info = self.custom_predator_starvation_scale_label.grid_info()
        self.custom_predator_starvation_scale_label.grid_forget()

        self.custom_predator_starvation_scale.grid(row=10, column=1, sticky='e', padx=25, pady=5, columnspan=3)
        self.custom_predator_starvation_scale_grid_info = self.custom_predator_starvation_scale.grid_info()
        self.custom_predator_starvation_scale.grid_forget()

        self.starvation_scale_marker.grid(row=10, column=0, sticky='e', columnspan=3, padx=(0, 185))
        self.starvation_scale_marker_grid_info = self.starvation_scale_marker.grid_info()
        self.starvation_scale_marker.grid_forget()

        self.custom_prey_label.grid(row=11, column=0, sticky='w', padx=30, pady=(10, 0))
        self.custom_prey_label_grid_info = self.custom_prey_label.grid_info()
        self.custom_prey_label.grid_forget()

        self.custom_prey_population_scale_label.grid(row=12, column=0, sticky='e', padx=34, columnspan=2)
        self.custom_prey_population_scale_label_grid_info = self.custom_prey_population_scale_label.grid_info()
        self.custom_prey_population_scale_label.grid_forget()

        self.custom_prey_population_scale.grid(row=12, column=1, sticky='e', padx=25, pady=5, columnspan=3)
        self.custom_prey_population_scale_grid_info = self.custom_prey_population_scale.grid_info()
        self.custom_prey_population_scale.grid_forget()

        self.prey_population_scale_marker.grid(row=12, column=0, sticky='e', columnspan=3, padx=(0, 185))
        self.prey_population_scale_marker_grid_info = self.prey_population_scale_marker.grid_info()
        self.prey_population_scale_marker.grid_forget()

        self.custom_prey_level_scale_label.grid(row=13, column=0, sticky='e', padx=34, pady=(5, 15), columnspan=2)
        self.custom_prey_level_scale_label_grid_info = self.custom_prey_level_scale_label.grid_info()
        self.custom_prey_level_scale_label.grid_forget()

        self.custom_prey_level_scale.grid(row=13, column=1, sticky='e', padx=25, pady=(5, 15), columnspan=3)
        self.custom_prey_level_scale_grid_info = self.custom_prey_level_scale.grid_info()
        self.custom_prey_level_scale.grid_forget()

        self.prey_level_scale_marker.grid(row=13, column=0, sticky='e', columnspan=3, padx=(0, 185), pady=(5, 15))
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
    total_populations: tuple[int, int]
    average_levels: tuple[float, float]
    average_hunger_level: float

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

        self.round_label = ttk.Label(self, text='Round 0', font=("Arial", 32, "underline"),
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

        self.predator_starvation_label = ttk.Label(self, text="Avg. Satiety:", font=("Arial", 14),
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

        self.predator_population_label.grid(column=0, row=2, padx=45, pady=5, sticky='w', columnspan=3)
        self.predator_population_marker.grid(column=1, row=2, padx=12, pady=5, sticky='e')

        self.predator_level_label.grid(column=0, row=3, padx=45, pady=5, sticky='w', columnspan=3)
        self.predator_level_marker.grid(column=1, row=3, padx=12, pady=5, sticky='e')

        self.predator_starvation_label.grid(column=0, row=4, padx=34, pady=5, sticky='w', columnspan=3)
        self.predator_starvation_marker.grid(column=1, row=4, padx=12, pady=5, sticky='e')

        self.prey_stats_label.grid(column=0, row=5, padx=12, pady=(18, 5), sticky='w', columnspan=2)

        self.prey_population_label.grid(column=0, row=6, padx=45, pady=5, sticky='w', columnspan=3)
        self.prey_population_marker.grid(column=1, row=6, padx=12, pady=5, sticky='e')

        self.prey_level_label.grid(column=0, row=7, padx=45, pady=5, sticky='w', columnspan=3)
        self.prey_level_marker.grid(column=1, row=7, padx=12, pady=5, sticky='e')

    def update_scoreboard(self):
        """
        Updates the scoreboard once the round's results have been shown

        If the score increased in comparison to the start of the round, the text is green
        If the score decreased in comparison to the start of the round, the text is red
        """

        # finding correct colors in response to previous score
        previous_predator_population = int(self.predator_population_marker.cget('text'))
        previous_prey_population = int(self.prey_population_marker.cget('text'))
        previous_predator_avg_level = float(self.predator_level_marker.cget('text'))
        previous_prey_avg_level = float(self.prey_level_marker.cget('text'))
        previous_avg_hunger_level = float(self.predator_starvation_marker.cget('text'))
        # finding new scores
        current_predator_population = int(self.total_populations[0])
        current_prey_population = int(self.total_populations[1])
        current_predator_avg_level = float(self.average_levels[0])
        current_prey_avg_level = float(self.average_levels[1])
        current_avg_hunger_level = float(self.average_hunger_level)
        
        # updating the labels with new scores and appropriate colors
        # green means a higher score, red means a lower score, gray means no change
        color = "green" if current_predator_population > previous_predator_population \
            else "red" if current_predator_population < previous_predator_population else "gray27"
        self.predator_population_marker.configure(text=current_predator_population, foreground=color)

        color = "green" if current_prey_population > previous_prey_population \
            else "red" if current_prey_population < previous_prey_population else "gray27"
        self.prey_population_marker.configure(text=current_prey_population, foreground=color)

        color = "green" if current_predator_avg_level > previous_predator_avg_level \
            else "red" if current_predator_avg_level < previous_predator_avg_level else "gray27"
        self.predator_level_marker.configure(text=current_predator_avg_level, foreground=color)

        color = "green" if current_prey_avg_level > previous_prey_avg_level \
            else "red" if current_prey_avg_level < previous_prey_avg_level else "gray27"
        self.prey_level_marker.configure(text=current_prey_avg_level, foreground=color)

        color = "green" if current_avg_hunger_level > previous_avg_hunger_level \
            else "red" if current_avg_hunger_level < previous_avg_hunger_level else "gray27"
        self.predator_starvation_marker.configure(text=current_avg_hunger_level, foreground=color)

    def uncolor_scoreboard_text(self):
        """
        Uncolors the scoreboard text color changes from the results of the round
        """
        self.predator_population_marker.configure(foreground='black')
        self.prey_population_marker.configure(foreground='black')
        self.predator_level_marker.configure(foreground='black')
        self.prey_level_marker.configure(foreground='black')
        self.predator_starvation_marker.configure(foreground='black')


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
        super().__init__(parent, bd=3, relief='solid', background=self.background_color)

        # creating and placing widgets within the boardkey frame
        self.create_widgets()
        self.place_widgets()
        # placing the boardkey below the scoreboard
        self.pack(padx=10, pady=(0, 10), fill='both', expand=True)
    
    def create_widgets(self):
        """
        Creates the widgets for the inside of this frame
        """       
        two_rounds_until_starvation_color = self.parent.parent.settings.two_rounds_until_starvation_color
        predator_outline = self.parent.parent.settings.predator_outline_color
        prey_color = self.parent.parent.settings.prey_background_color
        prey_outline = self.parent.parent.settings.prey_outline_color

        self.boardkey_label = ttk.Label(self, text='Board Key', font=("Arial", 29, "underline"),
                                     background=self.background_color, anchor='center')
        
        # creating predator pawn visual
        self.predator_pawn_label = ttk.Label(self, text='Predator Pawn:', font=("Arial", 16, "bold"),
                                             background=self.background_color)
        
        self.predator_pawn_object = tk.Frame(self, bd=0, relief='solid', background=two_rounds_until_starvation_color,
                                             highlightbackground=predator_outline, highlightthickness=3,
                                             width=60, height=60)
        
        self.predator_level_label = ttk.Label(self.predator_pawn_object, font=('Arial', 15, 'bold'),
                                     text='6', background=two_rounds_until_starvation_color, anchor='center')
        self.predator_birth_label = ttk.Label(self.predator_pawn_object, font=('Arial', 11, 'bold'),
                                     text='1', background=two_rounds_until_starvation_color)
        
        # adding description for predator visual
        self.predator_level_description = ttk.Label(self, text='6: Visual Acuity Level', font=("Arial", 8, 'bold'),
                                                    background=self.background_color)
        self.predator_birth_round_description = ttk.Label(self, text='1: Birth Round', font=("Arial", 8, 'bold'),
                                                          background=self.background_color)
        self.all_predator_colors_description = ttk.Label(self, text='Satiety Level (rounds until starvation):\n\n    Red = 1,  Orange = 2,  Yellow = 3+',
                                                    font=("Arial", 7, 'bold'), background=self.background_color)
        
        # creating prey pawn visual
        self.prey_pawn_label = ttk.Label(self, text='Prey Pawn:', font=("Arial", 16, "bold"),
                                             background=self.background_color)
        
        self.prey_pawn_object = tk.Canvas(self, background=self.background_color,
                                          width=65, height=65, highlightthickness=0)

        # must place prey object ahead of time to find the frame length
        self.prey_pawn_object.place(relx=0.03, rely=0.53, anchor='w')
        # updates and calculates size of the frame
        self.prey_pawn_object.update_idletasks()
        width, height = self.prey_pawn_object.winfo_width()-3, self.prey_pawn_object.winfo_height()-3
        x0, y0 = 3, 3  # top left coordinates of bounding rectangle
        x1, y1 = width, height  # bottom right coordinates of bounding rectangle
        self.prey_pawn_object.create_oval(x0, y0, x1, y1, fill=prey_color, outline=prey_outline, width=3)

        self.prey_level_label = ttk.Label(self.prey_pawn_object, font=('Arial', 15, 'bold'),
                                          text='4', background=prey_color, anchor='center')
        self.prey_birth_label = ttk.Label(self.prey_pawn_object, font=('Arial', 11, 'bold'),
                                          text='2', background=prey_color)
        
        # adding description for prey visual
        self.prey_level_description = ttk.Label(self, text='4: Camoflauge Level', font=("Arial", 8, 'bold'),
                                                background=self.background_color)
        self.prey_birth_round_description = ttk.Label(self, text='2: Birth Round', font=("Arial", 8, 'bold'),
                                                      background=self.background_color)
        self.prey_color_description = ttk.Label(self, text='(color has no significance)',
                                                font=("Arial", 8, 'bold'), background=self.background_color)

        # adding a section for square result symbols
        self.result_symbols_label = ttk.Label(self, text='Result Symbols:', font=("Arial", 16, "bold"),
                                             background=self.background_color)
        
        # predators win symbol
        self.predator_win_canvas = tk.Canvas(self, background='red', highlightthickness=0, width=40, height=40)
        # prey win symbol
        self.prey_win_canvas = tk.Canvas(self, background='green', highlightthickness=0, width=40, height=40)
        # tie symbol
        self.tie_canvas = tk.Canvas(self, background='gray', highlightthickness=0, width=40, height=40)
        # placing canvases ahead of time to be able to calculate their length
        self.predator_win_canvas.place(relx=0.07, rely=0.71)
        self.prey_win_canvas.place(relx=0.07, rely=0.795)
        self.tie_canvas.place(relx=0.07, rely=0.88)
        # updates and calculates size of the frame - all symbol keys have the same height and width
        self.predator_win_canvas.update_idletasks()
        frame_length = self.predator_win_canvas.winfo_width()
        line_symbol_padding = frame_length*0.2

        # placing lines for the symbols
        self.predator_win_canvas.create_line(line_symbol_padding, frame_length-line_symbol_padding,
                                        frame_length-line_symbol_padding, line_symbol_padding, fill='#800000',
                                        width=5)
        self.predator_win_canvas.create_line(line_symbol_padding, line_symbol_padding,
                                        frame_length-line_symbol_padding, frame_length-line_symbol_padding, fill='#800000',
                                        width=5)
        
        self.prey_win_canvas.create_line(line_symbol_padding, frame_length/2,
                                    frame_length-line_symbol_padding, frame_length/2, fill='#003300',
                                    width=5)
        self.prey_win_canvas.create_line(frame_length/2, line_symbol_padding, frame_length/2,
                                    frame_length-line_symbol_padding, fill='#003300',
                                    width=5)
        
        self.tie_canvas.create_line(line_symbol_padding, frame_length/2,
                                frame_length-line_symbol_padding, frame_length/2, fill='gray22',
                                width=5)
        
        # adding descriptions for the symbols
        self.predator_win_canvas_description = ttk.Label(self, text=':  Predators Win', font=("Arial", 12, 'bold'),
                                                         background=self.background_color)
        self.prey_win_canvas_description = ttk.Label(self, text=':  Prey Win', font=("Arial", 12, 'bold'),
                                                     background=self.background_color)
        self.tie_canvas_description = ttk.Label(self, text=': Tie', font=("Arial", 12, 'bold'),
                                                background=self.background_color)
        self.winner_description = ttk.Label(self, text='  winner is determined by the trophic\nteam with the highest net pop. growth',
                                            font=('Arial', 7, 'bold'), background=self.background_color)
        
    def place_widgets(self):
        """
        Places the widgets inside of this frame
        """
        # setting widgets
        self.boardkey_label.place(relx=0.5, rely=0.02, anchor='n')

        self.predator_pawn_label.place(relx=0.05, rely=0.15, anchor='w')
        self.predator_pawn_object.place(relx=0.05, rely=0.25, anchor='w')
        # predator level/birth labels inside predator object
        self.predator_birth_label.place(relx=0.15, rely=0.1)
        self.predator_level_label.place(relx=0.55, rely=0.4)
        # adding descriptions
        self.predator_birth_round_description.place(relx=0.38, rely=0.21)
        self.predator_level_description.place(relx=0.38, rely=0.27, anchor='w')
        self.all_predator_colors_description.place(relx=0.05, rely=0.32)

        self.prey_pawn_label.place(relx=0.05, rely=0.43, anchor='w')
        # prey pawn is placed ahead of time for winfo_height/width() to work
        # prey level/birth labels inside prey object
        self.prey_birth_label.place(relx=0.25, rely=0.18)
        self.prey_level_label.place(relx=0.5, rely=0.4)
        # adding descriptions
        self.prey_birth_round_description.place(relx=0.38, rely=0.49)
        self.prey_level_description.place(relx=0.38, rely=0.53)
        self.prey_color_description.place(relx=0.13, rely=0.6)
        
        self.result_symbols_label.place(relx=0.05, rely=0.67, anchor='w')
        # canvases placed ahead of time for frame lengths to be calculated

        # placing winner symbol descriptions
        self.predator_win_canvas_description.place(relx=0.3, rely=0.72)
        self.prey_win_canvas_description.place(relx=0.3, rely=0.805)
        self.tie_canvas_description.place(relx=0.3, rely=0.89)
        self.winner_description.place(relx=0.06, rely=0.95)