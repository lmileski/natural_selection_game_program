"""
Module: model

Classes for data storage/logic of the settings, the board, its squares, and animal pieces

Upon initialization, the CurrentSettings object holds every individual game setting as an attribute to be pulled by the model, view, and controller
The BoardModel holds a 2d array of SquareModel objects (board_length x board_length)
The SquareModel objects can each hold a max of 4 PredatorModel objects and 4 PreyModel objects
Both the PredatorModel and PreyModel classes share a couple similarities inherited by the Animal abstract base class

Model class heirarchy:

- BoardModel
    - SquareModel (# objects = # board squares)
        - PredatorModel(Animal) (# objects = # surviving predators in square)
        - PreyModel(Animal) (# objects = # surviving prey in square)

"""

from random import randrange
from collections import defaultdict
from abc import ABC, abstractmethod
from json import load, dump
from exceptions import SettingNotFound


class CurrentSettings:
    """
    Holds the game's most current settings
    Certain settings may be updated by the user with widget events
    Settings always start with the default upon initialization
    """
    # all the game's current settings in a 2-level dictionary
    all_settings_dict: dict
    # predator
    num_initial_predators: int
    predator_starting_level: int
    rounds_until_starvation: int
    min_rounds_until_starvation: int
    max_rounds_until_starvation: int
    one_round_until_starvation_color: str
    two_rounds_until_starvation_color: str
    three_or_more_rounds_until_starvation_color: str
    predator_symbol: str
    predator_outline_color: str
    # prey
    num_initial_prey: int
    prey_starting_level: int
    prey_symbol: str
    prey_outline_color: str
    prey_background_color: str
    # title
    title_font: str
    title_font_color: str
    title_background_color: str
    # left_menu
    widget_background_color: str
    scale_slider_color: str
    left_menu_background_color: str
    game_controls_background_color: str
    game_controls_text_label_color: str
    customize_settings_background_color: str
    customize_settings_text_label_color: str
    # right_menu
    right_menu_background_color: str
    scoreboard_background_color: str
    scoreboard_text_label_color: str
    boardkey_background_color: str
    boardkey_text_label_color: str
    # board
    customized_starting_animals: str
    board_length: int
    min_board_length: int
    max_board_length: int
    checkered_color1: str
    checkered_color2: str
    # change_of_rounds
    num_rounds: int
    pause_between_rounds: str
    delay_between_rounds: int
    random_pawn_placement_time: int
    delay_between_board_labels: int
    delay_between_square_results_labels: int
    countdown_background_color: str

    def __init__(self):
        """
        Assigns all default settings as attributes -

        Can be used by an existent object to reset all of its settings attributes to
        their default, which is pulled from the default configurations file
        """
        # default settings are pulled everytime the program is started
        self.all_settings_dict = CurrentSettings.default_settings()
        # assigning all the settings to their value for quick access
        for inner_dict in self.all_settings_dict.values():
            for second_key, value in inner_dict.items():
                setattr(self, second_key, value) # now an instance variable
    
    def update_settings(self, modified_setting: tuple[str, str, str | int]):
        """
        Updates two attributes of this object:
            - updates the all_settings_dict attribute by navigating the dictionary
            - updates the specific setting attribute
        
        Parameters:
            - modified_setting (tuple[str, str, str | int]):
                - (0): first key of the type of setting to be changed.
                - (1): second and last key of the type of setting to be changed.
                - (2): value of the new preference assigned by the user.
        """
        
        first_settings_key, second_settings_key, new_user_setting = modified_setting[0], modified_setting[1], modified_setting[2]
        inner_keys = [key for dicty in self.all_settings_dict.values() for key in dicty]
        # checking to make sure the setting is valid
        if first_settings_key not in self.all_settings_dict:
            raise SettingNotFound("First settings key doesn't exist")
        elif second_settings_key not in inner_keys:
            raise SettingNotFound("Second settings key doesn't exist")

        # modifying settings dictionary
        self.all_settings_dict[first_settings_key][second_settings_key] = new_user_setting
        # modifying the object's specific setting attribute
        setattr(self, second_settings_key, new_user_setting)

    def write_game_settings(self, settings_filename_to_update='game_settings_logs/user_configurations.json') -> None:
        """
        Writes the user's configurations used throughout the game
        to a the default user settings log file
        """

        with open(settings_filename_to_update, 'w') as f:
            dump(self.all_settings_dict, f, indent=4)

    @staticmethod
    def default_settings(default_settings_file_name="game_settings_logs/default_configurations.json") -> dict:
        """
        Resets the user's settings file to be identical to the default settings file
        Needed to copy over settings at the start of the game and for the tkinter reset settings command

        Parameters:
            - default_settings_file_name="game_settings_logs/default_configurations.json": name of the file holding the default settings
            - user_settings_file_name="game_settings_logs/user_configurations.json": name of the file holding the user's settings
        
        Returns:
            - (dict): dictionary with the default settings
        """
        # grabbing default settings
        with open(default_settings_file_name) as f:
            default_settings = load(f)

        return default_settings


class Animal(ABC):
    """
    Abstract Base Class for predator and prey objects
    """

    skill_level: int
    birth_round: int

    @abstractmethod
    def __init__(self, skill_level: int, birth_round: int):
        self.skill_level = skill_level
        self.birth_round = birth_round


class PredatorModel(Animal):
    """
    Predator gameboard object
    """

    skill_level: int
    birth_round: int
    rounds_until_starvation: int

    def __init__(self, skill_level: int, birth_round: int, default_rounds_until_starvation: int):
        super().__init__(skill_level, birth_round)
        self.rounds_until_starvation = default_rounds_until_starvation


class PreyModel(Animal):
    """
    Prey gameboard object
    """

    skill_level: int
    birth_round: int

    def __init__(self, skill_level: int, birth_round: int):
        super().__init__(skill_level, birth_round)
    

class SquareModel:
    """
    Represents a square on the board
    """
    board_position: tuple[int, int] # the coordinates of the square's position within board (eg. (1, 4))
    current_round: int
    default_rounds_until_starvation: int
    winner: int # assigned when the winner of the square is calculated
    prey: list['PreyModel'] # all the Prey objects within this square
    predators: list['PredatorModel'] # all the Predator objects within this square
    # lists of Predator and Prey objects that are being born/killed in the current round
    predator_births: list['PredatorModel']
    predator_deaths: list['PredatorModel']
    prey_births: list['PreyModel']
    prey_deaths: list['PreyModel']

    def __init__(self, board_position: tuple[int, int], default_rounds_until_starvation: int):
        self.board_position = board_position
        self.current_round = 1
        self.default_rounds_until_starvation = default_rounds_until_starvation
        self.prey = []
        self.predators = []
        self.predator_births = []
        self.predator_deaths = []
        self.prey_births = []
        self.prey_deaths = []

    def record_predator_eating_and_reproducing(self, parent: 'PredatorModel', eaten: 'PreyModel') -> None:
        """
        Modifies square's lists of births and deaths for predators and prey when predator eats prey
        Whenever predator reproduces, it always will have killed 1 prey
        Method reduces the redundancy of code needed for the determine_survivors() method

        Parameters:
            - parent (Predator): the Predator object that's eating
            - eaten (Prey): the prey object that's being eaten
        
        Preconditions:
            - parent.skill_level >= eaten.skill_level
        """
        assert parent.skill_level >= eaten.skill_level, "Improper function call - \
            Predators can only eat with skill level greater than or equal to the Prey"
        
        # predator dies after eating prey and reproducing
        self.predator_deaths.append(parent)
        self.prey_deaths.append(eaten)
        # skill levels of births are +1/-1 of parent's skill level
        self.predator_births.append(PredatorModel(parent.skill_level+1, self.current_round+1, self.default_rounds_until_starvation))
        # cannot go below zero - births are +0/+1 of parent's skill level if 0 - no upper limit
        if parent.skill_level == 0:
            self.predator_births.append(PredatorModel(parent.skill_level, self.current_round+1, self.default_rounds_until_starvation))
        else:
            self.predator_births.append(PredatorModel(parent.skill_level-1, self.current_round+1, self.default_rounds_until_starvation))

    def record_prey_reproducing(self, parent: 'PreyModel') -> None:
        """
        Modifies square's lists of births and deaths for prey when prey reproduces
        Method reduces the redundancy of code needed for the determine_survivors() method
        """
        # prey dies after reproducing
        self.prey_deaths.append(parent)
        # skill levels of births are +1/-1 of parent's skill level
        self.prey_births.append(PreyModel(parent.skill_level+1, self.current_round+1))
        # cannot go below zero - births are +0/+1 of parent's skill level if 0 - no upper limit
        if parent.skill_level == 0:
            self.prey_births.append(PreyModel(parent.skill_level, self.current_round+1))
        else:
            self.prey_births.append(PreyModel(parent.skill_level-1, self.current_round+1))
        # no changes are made if multiple prey objects in this square

    def enact_changes_to_births_and_deaths(self) -> None:
        """
        Modifies self.prey and self.predators by removing all dead prey and predators, respectively, who died in the round.
        Additionally, adds born prey and predators to self.prey and self.predators, respectively.
        """
        # enacting changes to births/deaths for upcoming round
        surviving_predators = []
        for predator in self.predators:
            if predator not in self.predator_deaths:
                surviving_predators.append(predator)
        surviving_predators.extend(self.predator_births)
        self.predators = surviving_predators # predators from square that will be randomly placed in next round

        surviving_prey = []
        for prey in self.prey:
            if prey not in self.prey_deaths:
                surviving_prey.append(prey)
        surviving_prey.extend(self.prey_births)
        self.prey = surviving_prey # prey from square that will be randomly placed in next round

    def determine_survivors(self) -> int:
        """
        Modifies the square's predators and prey list based off births and deaths.
        An in-depth explanation of the criteria for determining survivors and children
        can be found in the lab overview document.
        Additionally, an integer is returned, which corresponds to which animal team won the square.
        
        Parameters:
            - curr_round (int): the current round in the game - needed for initializing animal objects
            - default_rounds_until_starvation (int): the set number of rounds a predator has
            until it starves - needed for initializing Predator objects

        Returns:
            - (int): 1 if prey win, -1 if predators win, 0 if they tie
            Winner is whichever animal has the greatest increase in population
            Tie when each animal team's change in population is equal
            (eg. +1 predators/+2 prey - prey win, +0 predators/+0 prey - tie, +0 predators/-1 prey - predators win)
        """
        # sorts each starting animal list based off their skill level
        self.prey.sort(key=lambda prey: prey.skill_level) # ascending skill levels - lowest get eaten first
        self.predators.sort(reverse=True, key=lambda predator: predator.skill_level) # descending skill levels - highest eat first
        
        # determines what prey will be eaten, if any
        for predator in self.predators:
            predator_ate = False
            for prey in [surviving_prey for surviving_prey in self.prey if surviving_prey not in self.prey_deaths]: # only surviving prey can be eaten
                if predator.skill_level > prey.skill_level:
                    # marking predator's eaten status
                    predator_ate = True
                    # recording birth/death changes
                    self.record_predator_eating_and_reproducing(predator, prey)
                    # predator may only eat 1 prey per round
                    break

                elif prey.skill_level == predator.skill_level:
                    # 50/50 chance of being eaten if skill levels are equal
                    if randrange(2) == 0:
                        # marking predator's eaten status
                        predator_ate = True
                        # recording birth/death changes
                        self.record_predator_eating_and_reproducing(predator, prey)
                        # predator may only eat 1 prey per round
                        break
                    # else prey avoids attack
                # prey always avoids attack when it has a higher skill level

            if not predator_ate:
                predator.rounds_until_starvation -= 1 # predator is 1 round closer to starving if it hasn't eaten

        # if there is a sole prey object in square and hasn't been eaten, it reproduces
        if len(self.prey) == 1:
            prey = self.prey[0]
            if prey not in self.prey_deaths:
                # reproduces/modifies births/deaths when prey reproduces
                self.record_prey_reproducing(prey)

        # surviving predators who haven't eaten after default_rounds_until_starvation will die
        for alive_predator in [predator for predator in self.predators if predator not in self.predator_deaths]:
            if alive_predator.rounds_until_starvation == 0:
                self.predator_deaths.append(alive_predator) # not alive anymore :)

        # modifies self.prey and self.predators by removing dead animals and adding born animals
        self.enact_changes_to_births_and_deaths()

        # calculating which animal population has the greatest increase/smallest decrease in population - or tie
        predator_pop_change = len(self.predator_births) - len(self.predator_deaths)
        prey_pop_change = len(self.prey_births) - len(self.prey_deaths)
        # returning the winner - represented by an integer
        if predator_pop_change > prey_pop_change:
            return -1
        elif prey_pop_change > predator_pop_change:
            return 1
        else:
            return 0 # tie


class BoardModel:
    """
    Handles the logic/data for conducting the game's rounds

    Attributes are set upon their call by the controller when
    necessary to handle current game logic/determine visuals
    """

    current_round: int
    settings: 'CurrentSettings'
    survivors: tuple[list['PredatorModel'], list['PreyModel']]
    round_winner: str
    round_wins: dict[str, int]
    board: list[list['SquareModel']]
    previous_total_populations: tuple[int, int]
    total_populations: tuple[int, int]
    average_levels: tuple[float, float]
    average_hunger_level: float
    levels_to_populations: tuple[dict[int, int], dict[int, int]]


    def __init__(self, settings: 'CurrentSettings'):
        """
        Initializing settings, starting pieces, squares, and the board

        A new blank model is created upon the start of every game -
        attributes of squares/animals are dependent on the current settings
        """
        self.current_round = 0
        self.settings = settings
        self.survivors = ([], [])
        self.board = [[]]
        self.round_wins = {'predator': 0, 'prey': 0}
        # creating starting animals - either default or customized by user
        self.survivors = self.create_animals()
        # finding the starting stats
        self.calculate_total_populations()
        self.calculate_average_levels()
        self.calculate_average_hunger_level()
        # 2d array of Square objects - each inner list represents a column 
        self.board = [[SquareModel((x, y), self.settings.rounds_until_starvation) for y in range(self.settings.board_length)] for x in range(self.settings.board_length)]

    def create_animals(self) -> tuple[list['PredatorModel'], list['PreyModel']]:
        """
        Generates a list of Predator and a list of Prey objects for the start of the game
        Chart of default predator and prey initial populations-skill levels can be viewed in the lab overview
        User may customize the initial predator and prey populations to their desired sizes and skill levels

        Returns:
            - (tuple[list['Predator'], list['Prey']]): lists of starting predator (0) and prey (1) objects
        
        Preconditions (if user customized initial populations and skill levels):
            - predator levels >= 0
            - prey levels >= 0
            - 0 <= predator population <= number of squares * 4
            - 0 <= prey population <= number of squares * 4
        """
        animals: tuple[list['PredatorModel'], list['PreyModel']] = ([], [])
        # if user didn't choose to customize the starting levels of animals
        if self.settings.customized_starting_animals == "off":
            # 16 prey and 16 predator pieces are assigned levels based off default rules for the game
            # 4 predator and 4 prey pieces start at level 5 - 3 predator and 3 prey pieces start at level 4 and level 6, etc.
            # default initial levels are set between 2-8, inclusive
            curr_level = 2
            num_pieces = 1
            while curr_level <= 8:
                # adding certain number of animals at respective levels
                predators = [PredatorModel(curr_level, 1, self.settings.rounds_until_starvation) for _ in range(num_pieces)]
                prey = [PreyModel(curr_level, 1) for _ in range(num_pieces)]
                animals[0].extend(predators)
                animals[1].extend(prey)
                # conditions for loop's proper distribution of populations - levels
                if curr_level < 5:
                    num_pieces += 1
                else:
                    num_pieces -= 1   
                curr_level += 1

            if self.settings.board_length == 1:
                # special condition when board is 1 square - default starting animals must be cut
                predators = predators[:4]
                prey = prey[:4]
            
        # if user did choose to customize the starting levels of animals
        else:
            # checking preconditions
            assert self.settings.predator_starting_level >= 0
            assert self.settings.prey_starting_level >= 0
            assert 0 <= self.settings.num_initial_predators <= (self.settings.board_length ** 2) * 4
            assert 0 <= self.settings.num_initial_prey <= (self.settings.board_length ** 2) * 4
            # adding customized animals
            for _ in range(self.settings.num_initial_predators):
                animals[0].append(PredatorModel(self.settings.predator_starting_level, 0, self.settings.rounds_until_starvation))
            for _ in range(self.settings.num_initial_prey):
                animals[1].append(PreyModel(self.settings.prey_starting_level, 0))

        return animals

    def set_board(self) -> None:
        """
        Randomly sets the board based off last round's surviving animals
        Each square can hold a maximum of 4 predators and 4 prey

        Preconditions:
            - 0 <= Predator population <= board squares * 4 (squares can hold a maximum of 4 predators)
            - 0 <= Prey population <= board squares * 4 (squares can hold a maximum of 4 prey)
        """
        # checking population cap
        assert 0 <= len(self.survivors[0]) <= (self.settings.board_length ** 2) * 4
        assert 0 <= len(self.survivors[1]) <= (self.settings.board_length ** 2) * 4
        # randomly adding every surviving predator to board
        for predator in self.survivors[0]:
            random_x, random_y = (randrange(self.settings.board_length), randrange(self.settings.board_length))
            # ensuring there's 3 or less predators on random square before adding
            while len(self.board[random_x][random_y].predators) >= 4:
                random_x, random_y = (randrange(self.settings.board_length), randrange(self.settings.board_length))
            self.board[random_x][random_y].predators.append(predator)
        # randomly adding every surviving prey to board
        for p in self.survivors[1]:
            random_x, random_y = (randrange(self.settings.board_length), randrange(self.settings.board_length))
            # ensuring there's 3 or less prey on random square before adding
            while len(self.board[random_x][random_y].prey) >= 4:
                random_x, random_y = (randrange(self.settings.board_length), randrange(self.settings.board_length))
            self.board[random_x][random_y].prey.append(p)

    def clear_board(self) -> None:
        """
        Clear the board's squares of all animal objects and reset its round's death and birth lists
        Updates each square's current round +1
        To be used at the end of every round
        """
        self.current_round += 1
        for x in range(self.settings.board_length):
            for y in range(self.settings.board_length):
                self.board[x][y].current_round += 1
                self.board[x][y].predators = []
                self.board[x][y].prey = []
                self.board[x][y].predator_births = []
                self.board[x][y].predator_deaths = []
                self.board[x][y].prey_births = []
                self.board[x][y].prey_deaths = []

    def modify_board_survivors(self) -> None:
        """
        Modifies every square's surviving animals using the Square objects determine survivors method.
        Attributes the return int corresponding to which animal team won to its respective board square
        
        Additionally, updates self.survivors, which will be needed for setting the board in the next round.
        Both predators and prey have a population cap of 4 * number of squares.
        If either population is greater than this, their respective populations lowest level animals and killed
        and removed from self.survivors.

        Returns:
            - (list[list[int]]): a 2d array of integer which represents which animal won each square.
                Integer is 1 if prey win, -1 if predators win, 0 if they tie.
                Inner list refers to squares in each column from top to bottom.
                Outer list of lists refers to each column from left to right.
        """
        # resetting survivors
        self.survivors = ([], [])
        # walking through each square in the board
        for column in self.board:
            for square in column:
                # modifying square's animal survivors and taking the int of which team one - or tie
                winner_int = square.determine_survivors()
                setattr(square, 'winner', winner_int)
                # adding to survivors with square's new round updates
                self.survivors[0].extend(square.predators)
                self.survivors[1].extend(square.prey)

        # checking the population cap and removing lowest level animals over the limit
        population_cap = (self.settings.board_length ** 2) * 4
        num_living_predators = len(self.survivors[0])
        num_living_prey = len(self.survivors[1])
        # sorting predators and prey by descending level
        self.survivors[0].sort(reverse=True, key=lambda predator: predator.skill_level)
        self.survivors[1].sort(reverse=True, key=lambda prey: prey.skill_level)

        # converting to a list in order to cut elements
        actual_survivors: list[list['PredatorModel'] | list['PreyModel']] = list(self.survivors)
        # killing however many lowest level animals that are above the population limit
        if num_living_predators > population_cap:
            actual_survivors[0] = actual_survivors[0][:population_cap]
        if num_living_prey > population_cap:
            actual_survivors[1] = actual_survivors[1][:population_cap]
        
        # redefining self.survivors tuple with animals that survived the population_cap removal
        self.survivors = tuple(actual_survivors) # type: ignore

        # updating the game stats
        self.calculate_total_populations()
        self.calculate_average_levels()
        self.calculate_average_hunger_level()

    def calculate_total_populations(self) -> None:
        """
        Calculates population data of predators and prey - to be used at beginning of game and after each round.
        Calculates length of each list in self.survivors (tuple[list['Predator'], list['Prey']])
        Additionally, assigns the winning team of the round to whichever team had the highest net growth

        Determined values are stored in the total_populations attribute
            - tuple[int, int]:
                - (0) is the predator total population
                - (1) is the prey total population
        """
        predators, prey = self.survivors
        # determining if its the start of game - uninitialized
        if getattr(self, 'total_populations', None) == None and getattr(self, 'previous_total_populations', None) == None:
            # initializing both with the first population sizes
            self.total_populations = len(predators), len(prey)
            self.previous_total_populations = self.total_populations
        else:
            self.previous_total_populations = self.total_populations
            # finding newest populations
            self.total_populations = len(predators), len(prey)
            # finding the winner - team with the highest net growth
            predator_population_gain = self.total_populations[0] - self.previous_total_populations[0]
            prey_population_gain = self.total_populations[1] - self.previous_total_populations[1]
            if predator_population_gain > prey_population_gain:
                self.round_winner = 'predator'
                self.round_wins['predator'] += 1
            elif prey_population_gain > predator_population_gain:
                self.round_winner = 'prey'
                self.round_wins['prey'] += 1
            else:
                self.round_winner = 'tie'
    
    def calculate_average_levels(self) -> None:
        """
        Calculates the average skill level for all predators and all prey.
        Sums all the skill levels of animals from self.survivors (tuple[list['Predator'], list['Prey']])

        Determined values are stored in the average_levels attribute:
            - tuple[float, float]
                - (0) is the average of the predators' skill levels
                - (1) is the average of the preys' skill levels
        
        Doctests:
        >>> default_settings = CurrentSettings.default_settings()
        >>> board = BoardModel(default_settings)
        >>> board.survivors = ([Predator(4, 1, 2), Predator(3, 1, 3), Predator(6, 1, 2)],
        ... [Prey(6, 1), Prey(4, 1), Prey(7, 1)])
        >>> board.calculate_average_levels()
        (4.3, 5.7)
        """

        sum_predators_levels, sum_prey_levels = 0, 0
        predators, prey = self.survivors

        # totaling skill levels
        for predator in predators:
            sum_predators_levels += predator.skill_level
        
        for p in prey:
            sum_prey_levels += p.skill_level
        # calculating and returning average to 1 decimal place
        self.average_levels = round(sum_predators_levels/len(predators), 1), round(sum_prey_levels/len(prey), 1)

    def calculate_average_hunger_level(self) -> None:
        """
        Calculates the average hunger level of all predators on the board after
        the round has concluded
        Assigns the value to the object's averager_hunger_level attribute
        """
        sum_hunger_levels = 0
        for predator in self.survivors[0]:
            sum_hunger_levels += predator.rounds_until_starvation
        
        self.average_hunger_level = round(sum_hunger_levels/len(self.survivors[0]), 1)

    def calculate_levels_to_populations(self) -> None:
        """
        Calculates population data of predators and prey - to be used at beginning and end of game.
        Walks through self.survivors (tuple[list['Predator'], list['Prey']]) and finds each ones
        populations with respect to skill levels

        Determined values are stored in the levels_to_populations attribute
            - tuple[dict[int, int], dict[int, int]]
                - (0) (dict[int, int]) hold the predators population sizes with respect to skill level
                    - keys are the skill levels
                    - values are the population of predators at that skill level
                - (1) (dict[int, int]) hold the prey population sizes with respect to skill level
                    - keys are the skill levels
                    - values are the population of prey at that skill level
        """
        predators, prey = self.survivors
        # finding population with respect to skill levels
        predator_levels_to_population: dict[int, int] = defaultdict(int) # default values are 0
        for predator in predators:
            predator_levels_to_population[predator.skill_level] += 1
        
        prey_levels_to_population: dict[int, int] = defaultdict(int)
        for p in prey:
            prey_levels_to_population[p.skill_level] += 1

        self.levels_to_populations =  dict(predator_levels_to_population), dict(prey_levels_to_population)

    def find_winner(self):
        """
        Finds the winner of the game
        """
        return max(self.round_wins, key=lambda k: self.round_wins[k])