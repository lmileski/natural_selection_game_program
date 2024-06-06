"""
Pytest file for ensuring proper execution of controller.py methods
"""

import pytest
import sys
# pulling modules from shared parent directory
sys.path.append('../natural_selection_game_program')



if __name__ == '__main__':
    pytest.main(['tester_files/test_controller.py'])