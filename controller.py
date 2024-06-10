"""
Module: controller

Automation of EOSC-123 natural selection lab simulation

Author: Luke Mileski (lmileski@sandiego.edu)
"""

from tkinter import Event
import time
from model import BoardModel, CurrentSettings, SquareModel
from view import View


class Controller:
    """
    Intermediates between the model and view class
    """

    model: BoardModel # attributed upon click of the 'start game' button
    view: View
    settings: CurrentSettings

    def __init__(self, view: View, settings: CurrentSettings):
        """
        Initializing the controller's settings, model, view, and
        widget commands then starting the gui application
        """
        self.settings = settings
        self.view = view
        self.set_widget_commands()
        # starting gui
        self.view.mainloop()

    def conduct_round(self) -> None:
        """
        Conducts the data and visual changes for when the user starts any round
        """

    def assign_models_to_views(self, start_of_game: bool = False):
        """
        Assigns the board and square views their appropriate board or square model
        Needed for updating the round's data to display changes in surviving/born animals
        start_of_game boolean required for determining if square_view.create_animals() should be called

        create_animals() square method must be called at the time the results of the round are displayed -
        otherwise, the old animal views will be added to the square's list of animal views too early

        Parameters:
            - start_of_game (bool): True if called at the start of the game, false otherwise
        """
        # assigning board data to the View's board
        setattr(self.view.board_frame, 'board_data', self.model.board)
        # assigning each squares model data to its respective square view
        for x, column in enumerate(self.model.board):
            for y, square_model in enumerate(column):
                square_view = self.view.board_frame.board_visuals_2d[x][y]
                setattr(square_view, 'square_data', square_model)
                if start_of_game:
                    square_view.create_animals()

    def set_widget_commands(self) -> None:
        """
        Sets the commands of all tkinter widgets
        """

        widget_command_manager = WidgetCommands(self)

        self.view.left_menu_frame.game_controls.start_game_button['command'] = \
        widget_command_manager.start_game_button_command

        self.view.left_menu_frame.game_controls.reset_game_button['command'] = \
        widget_command_manager.reset_game_button_command

        self.view.left_menu_frame.game_controls.pause_button['command'] = \
        widget_command_manager.pause_game_button_command

        self.view.left_menu_frame.game_controls.start_round_button['command'] = \
        widget_command_manager.start_game_button_command

        self.view.left_menu_frame.game_controls.export_data_button['command'] = \
        widget_command_manager.export_data_to_excel_button_command

        self.view.left_menu_frame.game_controls.number_of_rounds_scale['command'] = \
        widget_command_manager.number_of_rounds_scale_command

        self.view.left_menu_frame.configurations.restore_default_settings_button['command'] = \
        widget_command_manager.restore_settings_button_command

        self.view.left_menu_frame.configurations.custom_board_checkbutton['command'] = \
        widget_command_manager.customize_board_checkbox_command

        self.view.left_menu_frame.configurations.custom_board_size_box.bind(
            '<<ComboboxSelected>>', widget_command_manager.board_size_combobox_command)

        self.view.left_menu_frame.configurations.custom_checker_color_box.bind(
            '<<ComboboxSelected>>', widget_command_manager.board_colors_combobox_command)

        self.view.left_menu_frame.configurations.custom_animals_checkbutton['command'] = \
        widget_command_manager.customize_starting_animals_checkbox_command

        self.view.left_menu_frame.configurations.custom_predator_level_scale['command'] = \
        widget_command_manager.predator_level_scale_command

        self.view.left_menu_frame.configurations.custom_predator_population_scale['command'] = \
        widget_command_manager.predator_population_scale_command

        self.view.left_menu_frame.configurations.custom_predator_starvation_scale['command'] = \
        widget_command_manager.predator_starvation_scale_command

        self.view.left_menu_frame.configurations.custom_prey_level_scale['command'] = \
        widget_command_manager.prey_level_scale_command

        self.view.left_menu_frame.configurations.custom_prey_population_scale['command'] = \
        widget_command_manager.prey_population_scale_command

        self.view.left_menu_frame.configurations.automatic_round_start_checkbutton['command'] = \
        widget_command_manager.automatic_round_start_checkbox_command

        self.view.left_menu_frame.configurations.custom_round_delay_scale['command'] = \
        widget_command_manager.round_delay_scale_command


class WidgetCommands:
    """
    Methods needed for the visual/logic changes in the program when a widget event occurs
    """

    def __init__(self, controller: Controller):
        """
        Sets up model, view, and controller for quick access
        """
        self.controller = controller
        # for ease of access
        self.view = self.controller.view
        self.game_controls_frame = self.view.left_menu_frame.game_controls
        self.configurations_frame = self.view.left_menu_frame.configurations
        self.scoreboard_frame = self.view.right_menu_frame.scoreboard
        self.settings = self.controller.settings
        self.default_settings = CurrentSettings.default_settings()

    def start_game_button_command(self) -> None:
        """
        Handles events when the user clicks the Start Game button
        """
        # setting up the model upon its initialization depending on the user's configurations
        self.controller.model = BoardModel(self.settings)
        self.model = self.controller.model
        # assigning all views their data
        self.controller.assign_models_to_views(start_of_game=True)
        # need to keep track of gui update times for visual to be in appropriate order
        self.current_gui_time = 0
        # disabling configurations/number of rounds scale
        self.change_configuration_widget_states('disabled')
        # changing game control buttons shown
        self.change_game_buttons_shown('start')
        # displaying the round and scattering pawns labels
        round_num = self.model.current_round
        self.view.board_frame.display_round_and_scattering_pawns_labels(round_num)
        self.current_gui_time += self.settings.delay_between_board_labels * 2
        # randomly drawing animals on the board
        self.view.board_frame.after(self.current_gui_time, self.view.board_frame.randomly_draw_all_animals)
        self.current_gui_time += self.settings.random_pawn_placement_time + 1500 # adding buffer
        # displaying countdown after gui has been fully updated with all animals
        self.view.board_frame.after(self.current_gui_time,
                                    self.view.board_frame.display_game_countdown, self.settings.delay_between_rounds)
        # adding to current gui time - GO label is 1250 milliseconds, 500 is the buffer
        self.current_gui_time += self.settings.delay_between_board_labels * self.settings.delay_between_rounds + 1250 + 500
        # calculating the results of the round
        self.model.modify_board_survivors()
        # assigning the resultant data to the board and square view objects
        self.controller.assign_models_to_views()
        # displaying the rounds results
        self.view.board_frame.after(self.current_gui_time, self.view.board_frame.diagonal_matrix_draw_all_results)



        # erasing all previous animal pawns from board 
        #self.erase_all_animals()
    
    def reset_game_button_command(self) -> None:
        """
        Handles events when the user clicks the Reset Game button
        """
        
    def pause_game_button_command(self) -> None:
        """
        Handles events when the user clicks the Pause Game button
        """
    
    def start_round_button_command(self) -> None:
        """
        Handles events when the user clicks the Start Round button
        """
    
    def export_data_to_excel_button_command(self) -> None:
        """
        Handles events when the user clicks the Export Game Data to Excel button
        """

    def change_configuration_widget_states(self, state: str) -> None:
        """
        Changes the state (normal or disabled) of all the scales and checkbuttons
        in the configurations frame and game controls frame
        Needed to prevent the user from changing settings in the middle of a game

        Parameters:
            - state (str): the state to change the widgets to - accepts either
                - 'normal' : activates all widgets
                - 'disabled' : deactivates all widgets
        """
        if state == 'disabled':
            self.game_controls_frame.number_of_rounds_scale.configure(state='disabled')

            self.configurations_frame.restore_default_settings_button.configure(state='disabled')
            
            self.configurations_frame.custom_board_checkbutton.configure(state='disabled')
            self.configurations_frame.custom_board_size_box.configure(state='disabled')
            self.configurations_frame.custom_checker_color_box.configure(state='disabled')
            
            self.configurations_frame.custom_animals_checkbutton.configure(state='disabled')
            self.configurations_frame.custom_predator_population_scale.configure(state='disabled')
            self.configurations_frame.custom_predator_level_scale.configure(state='disabled')
            self.configurations_frame.custom_predator_starvation_scale.configure(state='disabled')
            self.configurations_frame.custom_prey_population_scale.configure(state='disabled')
            self.configurations_frame.custom_prey_level_scale.configure(state='disabled')
            
            self.configurations_frame.automatic_round_start_checkbutton.configure(state='disabled')
            self.configurations_frame.custom_round_delay_scale.configure(state='disabled')
        
        elif state == 'normal':
            self.game_controls_frame.number_of_rounds_scale.configure(state='normal')

            self.configurations_frame.restore_default_settings_button.configure(state='normal')
            
            self.configurations_frame.custom_board_checkbutton.configure(state='normal')
            self.configurations_frame.custom_board_size_box.configure(state='normal')
            self.configurations_frame.custom_checker_color_box.configure(state='normal')
            
            self.configurations_frame.custom_animals_checkbutton.configure(state='normal')
            self.configurations_frame.custom_predator_population_scale.configure(state='normal')
            self.configurations_frame.custom_predator_level_scale.configure(state='normal')
            self.configurations_frame.custom_predator_starvation_scale.configure(state='normal')
            self.configurations_frame.custom_prey_population_scale.configure(state='normal')
            self.configurations_frame.custom_prey_level_scale.configure(state='normal')
            
            self.configurations_frame.automatic_round_start_checkbutton.configure(state='normal')
            self.configurations_frame.custom_round_delay_scale.configure(state='normal')
        
        else:
            raise ValueError("The state argument must either be 'normal' or 'disabled'")
    
    def change_game_buttons_shown(self, button_press: str) -> None:
        """
        Changes what buttons are shown to the user in the game controls panel

        Parameters:
            - button_press (str): the button clicked - accepts either
                - 'start' : hides certain buttons when the 'start game' button is pressed
                - 'reset' : hides certain buttons when the 'reset game' button is pressed
        """
        if button_press == 'start':
            self.game_controls_frame.start_game_button.grid_forget()

            self.game_controls_frame.reset_game_button.grid(
                **self.game_controls_frame.reset_game_button_grid_info)
            self.game_controls_frame.autofinish_game_button.grid(
                **self.game_controls_frame.autofinish_game_button_grid_info)
            self.game_controls_frame.pause_button.grid(
                **self.game_controls_frame.pause_button_grid_info)
        
        elif button_press == 'reset':
            self.game_controls_frame.start_game_button.grid(
                **self.game_controls_frame.start_game_button_grid_info)

            self.game_controls_frame.reset_game_button.grid_forget()
            self.game_controls_frame.autofinish_game_button.grid_forget()
            self.game_controls_frame.pause_button.grid_forget()
            self.game_controls_frame.start_round_button.grid_forget()
        
        else:
            raise ValueError("The button_press argument must either be 'start' or 'reset'")

    def update_scoreboard(self) -> None:
        """
        Updates the scoreboard once the round's results have been shown
        """
        scoreboard_frame = self.view.right_menu_frame.scoreboard

        scoreboard_frame.predator_population_marker.configure(
            text=self.model.total_populations[0],
        )
        scoreboard_frame.prey_population_marker.configure(
            text=self.model.total_populations[1]
        )
        scoreboard_frame.predator_level_marker.configure(
            text=self.model.average_levels[0]
        )
        scoreboard_frame.prey_level_marker.configure(
            text=self.model.average_levels[1]
        )
        scoreboard_frame.predator_starvation_marker.configure(
            text=self.model.average_hunger_level
        )


    def number_of_rounds_scale_command(self, value: str) -> None:
        """
        Handles events when the user toggles the number of rounds scale
        """
        # value is passed in as a string representation of a float
        new_value = round(float(value))
        self.settings.update_settings(('change_of_rounds', 'num_rounds', new_value))

        num_rounds_marker = self.game_controls_frame.number_of_rounds_scale_marker
        num_rounds_marker.configure(text=new_value)
    
    def restore_settings_button_command(self) -> None:
        """
        Handles events when the user clicks the Restore Default Settings button
        """
        # hiding all tkinter widgets aside from checkboxes - resetting their value and settings and updating visuals
        self.configurations_frame.custom_board_checkbox_value.set(0)
        self.customize_board_checkbox_command()

        self.configurations_frame.automatic_round_start_checkbox_value.set(0)
        self.automatic_round_start_checkbox_command()

        self.configurations_frame.custom_animals_checkbox_value.set(0)
        self.customize_starting_animals_checkbox_command()

        # removing advisory label and lock on animal checkbox if board was 1x1
        if self.configurations_frame.custom_animals_checkbutton.cget('state') == 'disabled':
            self.configurations_frame.custom_animals_checkbutton.configure(state='normal')
        # removing advisory label
        self.view.left_menu_frame.board_size_advisory_label.pack_forget()
    
    def customize_board_checkbox_command(self) -> None:
        """
        Handles events when the user clicks the Customize Board checkbox
        """
        # 1 when checked, 0 when unchecked
        box_checked = self.configurations_frame.custom_board_checkbox_value.get()
        if box_checked == 1: # true
            # showing widgets
            self.configurations_frame.custom_board_size_label.grid(
                **self.configurations_frame.custom_board_size_label_grid_info
            )
            self.configurations_frame.custom_board_size_box.grid(
                **self.configurations_frame.custom_board_size_box_grid_info
            )
            self.configurations_frame.custom_checker_color_label.grid(
                **self.configurations_frame.custom_checker_color_label_grid_info
            )
            self.configurations_frame.custom_checker_color_box.grid(
                **self.configurations_frame.custom_checker_color_box_grid_info
            )
        else:
            # hiding widgets
            self.configurations_frame.custom_board_size_label.grid_forget()

            self.configurations_frame.custom_board_size_box.grid_forget()

            self.configurations_frame.custom_checker_color_label.grid_forget()

            self.configurations_frame.custom_checker_color_box.grid_forget()

            # updating settings with default board size and colors
            specific_color1 = self.default_settings['board']['checkered_color1']
            specific_color2 = self.default_settings['board']['checkered_color2']

            self.settings.update_settings(('board', 'board_length', self.default_settings['board']['board_length']))
            self.settings.update_settings(('board', 'checkered_color1', specific_color1))
            self.settings.update_settings(('board', 'checkered_color2', specific_color2))

            # updating views and scale set for all widgets
            if specific_color1 == 'navajowhite4':
                specific_color1 = 'brown' # not specific anymore
            if specific_color2 == 'mint cream':
                specific_color2 = 'white' # not specific anymore

            self.configurations_frame.custom_board_size_box.set(f'{self.settings.board_length}x{self.settings.board_length}')
            self.configurations_frame.custom_checker_color_box.set(
                f'{(specific_color1).capitalize()} x {(specific_color2).capitalize()}')

            # redrawing board
            self.view.board_frame.draw_board()

    def board_size_combobox_command(self, event: Event) -> None:
        """
        Handles events when the user selects an option from the board size combobox
        """
        # grabbing the modified board size from the combobox of the event
        combobox = event.widget
        selection = combobox.get()
        new_board_length = int(selection[0])

        self.settings.update_settings(('board', 'board_length', new_board_length))
        self.view.board_frame.draw_board()
        # updating population scales/markers - population capacity depends on number of squares
        max_pop_capacity = (self.settings.board_length**2) * 4

        self.configurations_frame.custom_predator_population_scale.configure(to=max_pop_capacity)
        if int(self.configurations_frame.predator_population_scale_marker.cget('text')) > max_pop_capacity:
            self.predator_population_scale_command(str(max_pop_capacity))
        else:
            self.configurations_frame.custom_predator_population_scale.set(self.settings.num_initial_predators)

        self.configurations_frame.custom_prey_population_scale.configure(to=max_pop_capacity)
        if int(self.configurations_frame.prey_population_scale_marker.cget('text')) > max_pop_capacity:
            self.prey_population_scale_command(str(max_pop_capacity))
        else:
            self.configurations_frame.custom_prey_population_scale.set(self.settings.num_initial_prey)

        # special case where if the user selects a 1x1 board, they must customize starting animals - default pop > 1x1 board pop capacity
        if self.settings.board_length == 1:
            # checking animal customization checkbox
            self.configurations_frame.custom_animals_checkbox_value.set(1)
            # showing all its widgets
            self.customize_starting_animals_checkbox_command()
            # disabling the checkbox
            self.configurations_frame.custom_animals_checkbutton.configure(state='disabled')
            # adding advisory label
            self.view.left_menu_frame.board_size_advisory_label.pack(
                self.view.left_menu_frame.board_size_advisory_label_pack_info
            )
        else:
            # undisabling checkbox value if board length isn't 1x1
            if self.configurations_frame.custom_animals_checkbutton.cget('state') == 'disabled':
                self.configurations_frame.custom_animals_checkbutton.configure(state='normal')
            # removing advisory label
            self.view.left_menu_frame.board_size_advisory_label.pack_forget()

    def board_colors_combobox_command(self, event: Event) -> None:
        """
        Handles events when the user selects an option from the board colors combobox
        """
        # grabbing the modified board size from the combobox of the event
        combobox = event.widget
        selection = combobox.get()
        x_index = selection.index('x')
        checker_color1 = selection[:x_index-1].lower()
        checker_color2 = selection[x_index+2:].lower()

        # finding specific color names
        if checker_color1 == 'brown':
            checker_color1 = 'navajowhite4'
        elif checker_color1 == 'gray':
            checker_color1 = 'light slate gray'
        elif checker_color1 == 'blue':
            checker_color1 = 'sky blue'
        else: # pink
            checker_color1 = 'thistle'

        # only checker color 2 option is white - this color is close enough
        if checker_color2 == 'white':
            checker_color2 = 'mint cream'
        else: # pink
            checker_color2 = 'thistle' 
        
        self.settings.update_settings(('board', 'checkered_color1', checker_color1))
        self.settings.update_settings(('board', 'checkered_color2', checker_color2))
        # redrawing the board
        self.view.board_frame.draw_board()
    
    def automatic_round_start_checkbox_command(self) -> None:
        """
        Handles when the user clicks the Automatic Round Start checkbox
        """
        # 1 if checked, 0 if not
        box_checked = self.view.left_menu_frame.configurations.automatic_round_start_checkbox_value.get()
        if box_checked == 1: # true
            # showing widgets
            self.settings.update_settings(('change_of_rounds', 'pause_between_rounds', 'off'))

            self.configurations_frame.round_delay_label.grid(
                **self.configurations_frame.round_delay_label_grid_info
            )
            self.configurations_frame.custom_round_delay_scale.grid(
                **self.configurations_frame.custom_round_delay_scale_grid_info
            )
            self.configurations_frame.custom_round_delay_scale_marker.grid(
                **self.configurations_frame.custom_round_delay_scale_marker_grid_info
            )
        else: # false
            # hiding widgets
            self.configurations_frame.round_delay_label.grid_forget()

            self.configurations_frame.custom_round_delay_scale.grid_forget()

            self.configurations_frame.custom_round_delay_scale_marker.grid_forget()

            # updating settings with default round delay
            self.settings.update_settings(('change_of_rounds', 'pause_between_rounds', 'off'))
            self.settings.update_settings(('change_of_rounds', 'delay_between_rounds',
                                           self.default_settings['change_of_rounds']['delay_between_rounds']))
            # updating scale views and markers to default
            self.configurations_frame.custom_round_delay_scale_marker.configure(text=f'{self.settings.delay_between_rounds}s')
            self.configurations_frame.custom_round_delay_scale.set(self.settings.delay_between_rounds)

    def round_delay_scale_command(self, value: str) -> None:
        """
        Handles events when the user toggles the round delay scale
        """
        # value is passed in as a string representation of a float
        new_value = round(float(value))
        self.settings.update_settings(('change_of_rounds',
                                       'delay_between_rounds', new_value))
    
        round_delay_marker = self.configurations_frame.custom_round_delay_scale_marker
        round_delay_marker.configure(text=f'{new_value}s')

    def customize_starting_animals_checkbox_command(self) -> None:
        """
        Handles events when the user clicks the Customize Starting Animals checkbox
        """
        # 1 if checked, 0 if not
        box_checked = self.configurations_frame.custom_animals_checkbox_value.get()

        if box_checked == 1: # true
            self.settings.update_settings(('board', 'customized_starting_animals', 'on'))

            self.configurations_frame.custom_predator_label.grid(
                **self.configurations_frame.custom_predator_label_grid_info
            )

            self.configurations_frame.custom_predator_population_scale_label.grid(
                **self.configurations_frame.custom_predator_population_scale_label_grid_info
            )

            self.configurations_frame.custom_predator_population_scale.grid(
                **self.configurations_frame.custom_predator_population_scale_grid_info
            )

            self.configurations_frame.predator_population_scale_marker.grid(
                **self.configurations_frame.predator_population_scale_marker_grid_info
            )

            self.configurations_frame.custom_predator_level_scale_label.grid(
                **self.configurations_frame.custom_predator_level_scale_label_grid_info
            )

            self.configurations_frame.custom_predator_level_scale.grid(
                **self.configurations_frame.custom_predator_level_scale_grid_info
            )

            self.configurations_frame.predator_level_scale_marker.grid(
                self.configurations_frame.predator_level_scale_marker_grid_info
            )

            self.configurations_frame.custom_predator_starvation_scale_label.grid(
                **self.configurations_frame.custom_predator_starvation_scale_label_grid_info
            )

            self.configurations_frame.custom_predator_starvation_scale.grid(
                **self.configurations_frame.custom_predator_starvation_scale_grid_info
            )

            self.configurations_frame.starvation_scale_marker.grid(
                **self.configurations_frame.starvation_scale_marker_grid_info
            )

            self.configurations_frame.custom_prey_label.grid(
                **self.configurations_frame.custom_prey_label_grid_info
            )

            self.configurations_frame.custom_prey_population_scale_label.grid(
                **self.configurations_frame.custom_prey_population_scale_label_grid_info
            )

            self.configurations_frame.custom_prey_population_scale.grid(
                **self.configurations_frame.custom_prey_population_scale_grid_info
            )

            self.configurations_frame.prey_population_scale_marker.grid(
                **self.configurations_frame.prey_population_scale_marker_grid_info
            )

            self.configurations_frame.custom_prey_level_scale_label.grid(
                **self.configurations_frame.custom_prey_level_scale_label_grid_info
            )

            self.configurations_frame.custom_prey_level_scale.grid(
                **self.configurations_frame.custom_prey_level_scale_grid_info
            )

            self.configurations_frame.prey_level_scale_marker.grid(
                **self.configurations_frame.prey_level_scale_marker_grid_info
            )

        else: # false
            # hiding widgets
            self.settings.update_settings(('board', 'customized_starting_animals', 'off'))

            self.configurations_frame.custom_predator_label.grid_forget()

            self.configurations_frame.custom_predator_population_scale_label.grid_forget()

            self.configurations_frame.custom_predator_population_scale.grid_forget()

            self.configurations_frame.predator_population_scale_marker.grid_forget()

            self.configurations_frame.custom_predator_level_scale_label.grid_forget()

            self.configurations_frame.custom_predator_level_scale.grid_forget()

            self.configurations_frame.predator_level_scale_marker.grid_forget()

            self.configurations_frame.custom_predator_starvation_scale_label.grid_forget()

            self.configurations_frame.custom_predator_starvation_scale.grid_forget()

            self.configurations_frame.starvation_scale_marker.grid_forget()

            self.configurations_frame.custom_prey_label.grid_forget()

            self.configurations_frame.custom_prey_population_scale_label.grid_forget()

            self.configurations_frame.custom_prey_population_scale.grid_forget()

            self.configurations_frame.prey_population_scale_marker.grid_forget()

            self.configurations_frame.custom_prey_level_scale_label.grid_forget()

            self.configurations_frame.custom_prey_level_scale.grid_forget()

            self.configurations_frame.prey_level_scale_marker.grid_forget()

            # restoring all default animal starting stats and
            # updating scales and scale markers to their default
            self.predator_population_scale_command(self.default_settings['predator']['num_initial_predators'])
            self.configurations_frame.custom_predator_population_scale.set(self.settings.num_initial_predators)

            self.predator_level_scale_command(self.default_settings['predator']['predator_starting_level'])
            self.configurations_frame.custom_predator_level_scale.set(self.settings.predator_starting_level)

            self.predator_starvation_scale_command(self.default_settings['predator']['rounds_until_starvation'])
            self.configurations_frame.custom_predator_starvation_scale.set(self.settings.rounds_until_starvation)

            self.prey_population_scale_command(self.default_settings['prey']['num_initial_prey'])
            self.configurations_frame.custom_prey_population_scale.set(self.settings.num_initial_prey)

            self.prey_level_scale_command(self.default_settings['prey']['prey_starting_level'])
            self.configurations_frame.custom_prey_level_scale.set(self.settings.prey_starting_level)
 
    def predator_population_scale_command(self, value: str) -> None:
        """
        Handles events when the user toggles the predator population scale
        """
        # value is passed in as a string representation of a float
        new_value = round(float(value))
        self.settings.update_settings(('predator', 'num_initial_predators', new_value))
        # modifying configurations display
        population_scale_marker = self.configurations_frame.predator_population_scale_marker
        population_scale_marker.configure(text=new_value)
        # modifying scoreboard display
        scoreboard_level_marker = self.scoreboard_frame.predator_population_marker
        scoreboard_level_marker.configure(text=new_value)

    def predator_level_scale_command(self, value: str) -> None:
        """
        Handles events when the user toggles the predator level scale
        """
        # value is passed in as a string representation of a float
        new_value = round(float(value))
        self.settings.update_settings(('predator', 'predator_starting_level', new_value))
        # modifying configurations display
        level_scale_marker = self.configurations_frame.predator_level_scale_marker
        level_scale_marker.configure(text=new_value)
        # modifying scoreboard display
        scoreboard_level_marker = self.scoreboard_frame.predator_level_marker
        scoreboard_level_marker.configure(text=new_value)

    def predator_starvation_scale_command(self, value: str) -> None:
        """
        Handles events when the user toggles the predator rounds until starvation scale
        """
        # value is passed in as a string representation of a float
        new_value = round(float(value))
        self.settings.update_settings(('predator', 'rounds_until_starvation', new_value))
        # modifying configurations display
        starvation_scale_marker = self.configurations_frame.starvation_scale_marker
        starvation_scale_marker.configure(text=new_value)
        # modifying scoreboard display
        scoreboard_starvation_marker = self.scoreboard_frame.predator_starvation_marker
        scoreboard_starvation_marker.configure(text=new_value)
            
    def prey_population_scale_command(self, value: str) -> None:
        """
        Handles events when the user toggles the prey population scale
        """
        # value is passed in as a string representation of a float
        new_value = round(float(value))
        self.settings.update_settings(('prey', 'num_initial_prey', new_value))
        # modifying configurations display
        population_scale_marker = self.configurations_frame.prey_population_scale_marker
        population_scale_marker.configure(text=new_value)
        # modifying scoreboard display
        scoreboard_population_marker = self.scoreboard_frame.prey_population_marker
        scoreboard_population_marker.configure(text=new_value)

    def prey_level_scale_command(self, value: str) -> None:
        """
        Handles events when the user toggles the prey level scale
        """
        # value is passed in as a string representation of a float
        new_value = round(float(value))
        self.settings.update_settings(('prey', 'prey_starting_level', new_value))
        # modifying configurations display
        level_scale_marker = self.configurations_frame.prey_level_scale_marker
        level_scale_marker.configure(text=new_value)
        # modifying scoreboard display
        scoreboard_level_marker = self.scoreboard_frame.prey_level_marker
        scoreboard_level_marker.configure(text=new_value)


if __name__ == "__main__":
    settings = CurrentSettings()
    # setting up model and view
    model = BoardModel(settings)
    view = View(settings)
    # controller creates model upon creation 
    controller = Controller(view, settings)