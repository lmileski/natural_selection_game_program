"""
Pytest file for tests cases of the determine_survivors() square method along with its helper square methods, which includes:
    - Square.record_predator_eating_and_reproducing()
    - Square.record_prey_reproducing()
    - Square.enact_changes_to_births_and_deaths()

Test cases check to make sure the following Square instance variables are properly updated (checks count, skill levels, and rounds_until_starvation):
    - prey (list[Prey]): The Prey objects that are alive/born after the end of the round
    - predators (list[Predator]): The Predator objects that are alive/born after the end of the round

Test cases also check to make sure the integer value corresponding to which animal team won is correct:
    - 1 if the prey win
    - -1 if the predators win
    - 0 if they tie
"""
import pytest
import sys
# pulling modules from shared parent directory
sys.path.append('../natural_selection_game_program')
from model import PredatorModel, PreyModel, SquareModel

def test_determine_survivors_case1():
    """
    No prey and no predators -> tie
    """
    square = SquareModel((0, 0), 2)
    assert square.determine_survivors() == 0
    assert square.prey == []
    assert square.predators == []

def test_determine_survivors_case2():
    """
    1 prey and 0 predators -> prey win and prey object reproduces
    Prey parent has a skill level > 0
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(1, 1)]
    assert square.determine_survivors() == 1
    assert len(square.prey) == 2
    prey_1_up, prey_1_down = square.prey
    assert prey_1_up.skill_level == 2
    assert prey_1_down.skill_level == 0
    assert square.predators == []

def test_determine_survivors_case3():
    """
    1 prey and 0 predators -> prey win and prey object reproduces
    Prey parent's skill level == 0
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(0, 1)]
    assert square.determine_survivors() == 1
    assert len(square.prey) == 2
    prey_1_up, prey_equal = square.prey
    assert prey_1_up.skill_level == 1
    assert prey_equal.skill_level == 0
    assert square.predators == []

def test_determine_survivors_case4():
    """
    0 prey and 1 predator -> tie
    Predator's rounds_until_starvation > 1 (must decrease by 1)
    """
    square = SquareModel((0, 0), 2)
    square.predators = [PredatorModel(0, 1, 2)]
    assert square.determine_survivors() == 0
    assert square.prey == []
    assert len(square.predators) == 1
    assert square.predators[0].rounds_until_starvation == 1

def test_determine_survivors_case5():
    """
    0 prey and 1 predator -> prey win
    Predator's rounds_until_starvation == 1 (dies after not eating during the round)
    """
    square = SquareModel((0, 0), 2)
    square.predators = [PredatorModel(1, 1, 1)]
    assert square.determine_survivors() == 1
    assert square.prey == []
    assert square.predators == []

def test_determine_survivors_case6():
    """
    1 prey and 1 predator -> prey win and prey object reproduces
    Prey's skill_level > Predator's skill_level
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(10, 1)]
    square.predators = [PredatorModel(5, 1, 2)]
    assert square.determine_survivors() == 1
    assert len(square.prey) == 2
    assert len(square.predators) == 1

def test_determine_survivors_case7():
    """
    1 prey and 1 predator -> predators win and predator object reproduces
    Predators's skill_level > Prey's skill_level
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(2, 1)]
    square.predators = [PredatorModel(3, 1, 2)]
    assert square.determine_survivors() == -1
    assert len(square.prey) == 0
    assert len(square.predators) == 2

def test_determine_survivors_case8():
    """
    1 prey and 2 predators -> predators win (1 predator object eats prey, 1 predator object starves)
    1 Predators's skill_level > Prey's skill_level
    1 Predator's rounds_until_starvation == 1
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(2, 1)]
    square.predators = [PredatorModel(3, 1, 2), PredatorModel(0, 1, 1)]
    assert square.determine_survivors() == -1
    assert len(square.prey) == 0
    assert len(square.predators) == 2

def test_determine_survivors_case9():
    """
    2 prey and 1 predator -> predators win (predator object eats and reproduces)
    Predators's skill_level > one of the Prey's skill_level
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(2, 1), PreyModel(4, 1)]
    square.predators = [PredatorModel(3, 1, 2)]
    assert square.determine_survivors() == -1
    assert len(square.prey) == 1
    assert len(square.predators) == 2

def test_determine_survivors_case10():
    """
    2 prey and 1 predator -> tie (no change in population occurs)
    Predators's skill_level < both of the Prey's skill_level
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(2, 1), PreyModel(3, 1)]
    square.predators = [PredatorModel(1, 1, 2)]
    assert square.determine_survivors() == 0
    assert len(square.prey) == 2
    assert len(square.predators) == 1

def test_determine_survivors_case11():
    """
    2 prey and 2 predator -> predators win (both predators eat)
    Predators' skill_levels > both of the Prey's skill_level
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(2, 1), PreyModel(3, 1)]
    square.predators = [PredatorModel(4, 1, 2), PredatorModel(5, 1, 1)]
    assert square.determine_survivors() == -1
    assert len(square.prey) == 0
    assert len(square.predators) == 4

def test_determine_survivors_case12():
    """
    1 prey and 3 predators -> tie (prey is eaten and 2 predators starve)
    One Predator's skill_levels > Prey's skill_level
    Two other Predator's rounds_until_starvation == 1
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(2, 1)]
    square.predators = [PredatorModel(4, 1, 1), PredatorModel(5, 1, 1), PredatorModel(6, 1, 1)]
    assert square.determine_survivors() == 0
    assert len(square.prey) == 0
    assert len(square.predators) == 2

def test_determine_survivors_case13():
    """
    3 prey and 3 predators -> predators win (2 prey are eaten)
    Two Predator's skill_levels > two Prey's skill_level
    Testing to make sure prey with lowest levels are eaten first and predators with
    highest skill levels eat first
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(8, 1), PreyModel(2, 1), PreyModel(1, 1)]
    square.predators = [PredatorModel(4, 1, 2), PredatorModel(5, 1, 1), PredatorModel(6, 1, 1)]
    assert square.determine_survivors() == -1
    assert len(square.prey) == 1
    assert square.prey[0].skill_level == 8
    assert len(square.predators) == 5

def test_determine_survivors_case14():
    """
    4 prey and 4 predators -> tie (2 prey are eaten and 2 predators starve)
    Two Predator's skill_levels > two Prey's skill_level
    Two Predator's rounds_until_starvation == 1
    """
    square = SquareModel((0, 0), 2)
    square.prey = [PreyModel(10, 1), PreyModel(9, 1), PreyModel(5, 1), PreyModel(6, 1)]
    square.predators = [PredatorModel(4, 1, 1), PredatorModel(5, 1, 1), PredatorModel(8, 1, 1), PredatorModel(7, 1, 1)]
    assert square.determine_survivors() == -1
    assert len(square.prey) == 2
    assert len(square.predators) == 4


if __name__ == '__main__':
    pytest.main(['tester_files/test_determine_survivors.py'])