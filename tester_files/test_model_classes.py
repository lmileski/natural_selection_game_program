"""
Pytest file for ensuring proper execution of the Board class methods
"""

import pytest
from collections import defaultdict
import sys
# pulling modules from shared parent directory
sys.path.append('../natural_selection_game_program')
from model import BoardModel, CurrentSettings
from exceptions import SettingNotFound
from controller import Controller
from model import BoardModel, CurrentSettings
from view import View

def test_update_settings():
    """
    Tests the CurrentSettings update_settings() static method
    """
    # create mvc
    modified_settings = CurrentSettings() # grabs default settings dict
    model = BoardModel(modified_settings)
    view = View(modified_settings)
    controller = Controller(model, view, modified_settings)

    # ensuring model, view, and controller are all updated
    modified_settings.update_settings(('predator', 'num_initial_predators', 10))
    assert view.settings.num_initial_predators == 10
    assert model.settings.num_initial_predators == 10
    assert controller.settings.num_initial_predators == 10

    # making non-viable changes to settings
    with pytest.raises(SettingNotFound):
        modified_settings.update_settings(('non-existent-key', 'num_initial_predators', 10))

    with pytest.raises(SettingNotFound):
        modified_settings.update_settings(('predator', 'non-existent-key', 10))

def test_create_animals():
    """
    Tests create_animals() to ensure it works with default settings and user customizations
    """
    settings = CurrentSettings()
    board = BoardModel(settings)

    starting_predators, starting_prey = board.create_animals()
    # counting number of predators and prey at each level
    predator_levels_to_populations = defaultdict(int)
    prey_levels_to_populations = defaultdict(int)
    for predator in starting_predators:
        predator_levels_to_populations[predator.skill_level] += 1
    for prey in starting_prey:
        prey_levels_to_populations[prey.skill_level] += 1
    # ensuring their counts are as expected
    assert dict(predator_levels_to_populations) == {2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 2, 8:1}
    assert dict(prey_levels_to_populations) == {2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 2, 8:1}

    # testing with user-customized starting animal populations and levels
    customized_settings = settings
    customized_settings.customized_starting_animals = 'on'
    customized_settings.num_initial_predators = 10
    customized_settings.num_initial_prey = 5
    customized_settings.predator_starting_level = 6
    customized_settings.prey_starting_level = 8
    customized_board = BoardModel(customized_settings)

    starting_predators, starting_prey = customized_board.create_animals()
    # counting number of predators and prey at each level
    predator_levels_to_populations = defaultdict(int)
    prey_levels_to_populations = defaultdict(int)
    for predator in starting_predators:
        predator_levels_to_populations[predator.skill_level] += 1
    for prey in starting_prey:
        prey_levels_to_populations[prey.skill_level] += 1
    # ensuring their counts are as expected
    assert dict(predator_levels_to_populations) == {6: 10}
    assert dict(prey_levels_to_populations) == {8: 5}

if __name__ == '__main__':
    pytest.main(['tester_files/test_model_classes.py'])