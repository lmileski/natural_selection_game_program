"""
Pytest file for ensuring proper execution of model.py functions
"""

import pytest
import sys
# pulling modules from shared parent directory
sys.path.append('../natural_selection_game_program')
from model_helpers import record_round_data, record_start_and_end_data


def test_record_round_data():
    """
    Tests record_round_data() for a 2-round game
    Tests only to make sure no errors are thrown in execution of the function
    Correctness of format/values inserted into respective file will be judged after execution
    """
    # recording first rounds starting data
    starting_first_round_data = (1, (16, 16), (5, 5), 'predators')
    record_round_data(starting_first_round_data)

    # recording second rounds starting data
    starting_second_round_data = (2, (14, 17), (5.3, 5.5), 'prey')
    record_round_data(starting_second_round_data)

    # recording second rounds ending data
    end_of_second_round_data = (3, (12, 19), (5.7, 5.9), 'tie') # ending results will be marked as number of rounds completed +1

    record_round_data(end_of_second_round_data)

def test_record_start_and_end_data():
    """
    Tests record_start_and_end_data() with the beginning and end of game results
    Tests only to make sure no errors are thrown in execution of the function
    Correctness of format/values inserted into respective file will be judged after execution
    """
    # using default starting skill levels to populations settings
    starting_skill_levels_to_populations = (
        {2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 2, 8: 1}, # predators
        {2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 2, 8: 1}  # prey
        )
    # recording start data
    record_start_and_end_data(starting_skill_levels_to_populations, True)

    ending_skill_levels_to_populations = (
        {0: 1, 2: 2, 4: 3, 6: 3, 7: 3, 9: 1}, # predators
        {0: 1, 1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 7, 10: 1}  # prey
        )
    # recording end data
    record_start_and_end_data(ending_skill_levels_to_populations, False)

if __name__ == '__main__':
    pytest.main(['tester_files/test_model_helpers.py'])