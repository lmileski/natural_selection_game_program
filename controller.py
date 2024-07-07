"""
Module: controller

Automation of EOSC-123 natural selection lab simulation

Author: Luke Mileski (lmileski@sandiego.edu)
"""

from tkinter import Event
from typing import Callable
from model import BoardModel, CurrentSettings, SquareModel
from view import View
import model_helpers


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

    def assign_models_to_views(self, start_of_round = False):
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
        # assigning stats to the scoreboard
        setattr(self.view.right_menu_frame.scoreboard, 'total_populations', self.model.total_populations)
        setattr(self.view.right_menu_frame.scoreboard, 'average_levels', self.model.average_levels)
        setattr(self.view.right_menu_frame.scoreboard, 'average_hunger_level', self.model.average_hunger_level)
        # assigning each squares model data to its respective square view
        for x, column in enumerate(self.model.board):
            for y, square_model in enumerate(column):
                square_view = self.view.board_frame.board_visuals_2d[x][y]
                setattr(square_view, 'square_data', square_model)
                # assigns the square view their animal view objects
                if start_of_round:
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

        self.view.left_menu_frame.game_controls.autofinish_game_button['command'] = \
        widget_command_manager.autofinish_game_button_command

        self.view.left_menu_frame.game_controls.start_round_button['command'] = \
        widget_command_manager.start_round_button_command

        self.view.left_menu_frame.game_controls.finish_round_button['command'] = \
        widget_command_manager.finish_round_button_command

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

    next_game_command: Callable # required to keep track of stage in mainloop for the autofinish game button

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
        # finding the starting game data and recording the round 0 data
        self.initial_levels_to_populations = self.model.levels_to_populations
        model_helpers.record_round_data(
            (self.model.current_round, self.model.total_populations, self.model.average_levels, 'n/a')
        )
        # recording the user's game configurations
        self.settings.write_game_settings()
        # need to keep track of gui update times for visual to be in appropriate order
        self.current_gui_time = 0
        # increasing round number
        self.model.current_round += 1
        # disabling configurations/number of rounds scale
        self.change_configuration_widget_states('disabled')
        # changing game control buttons shown
        self.change_game_buttons_shown('start')
        # displaying scatter pawns label and doing so
        self.scatter_pawns()
        # recording the start round button command as the next command to be called - for autofinish game button
        setattr(self, 'next_game_command', self.start_round_button_command)


    # mainloop for the game's rounds - performed either manually or automatically (depends on user configurations)
    def scatter_pawns(self) -> None:
        """
        Scatters the game pawns
        """
        # assigning squares their animals
        self.model.set_board()
        # integrating views and models
        self.controller.assign_models_to_views(True)

        if self.settings.autofinish_game == 'off':
            # displaying the round and scattering pawns labels
            display_round_label_task = self.view.after(
                self.current_gui_time, lambda: self.view.board_frame.display_round_label(self.model.current_round))
            self.view.board_frame.scheduled_tasks.append(display_round_label_task)
            update_round_label_task = self.view.after(
                    self.current_gui_time, lambda: self.view.right_menu_frame.scoreboard.round_label.configure(text=f'Round {self.model.current_round}'))
            self.view.board_frame.scheduled_tasks.append(update_round_label_task)
            
            self.current_gui_time += self.settings.delay_between_board_labels

            display_scattering_pawns_label_task = self.view.after(self.current_gui_time, self.view.board_frame.display_scattering_pawns_label)
            self.view.board_frame.scheduled_tasks.append(display_scattering_pawns_label_task)

            self.current_gui_time += self.settings.delay_between_board_labels + 500 # buffer
            # randomly drawing animals on the board
            randomly_draw_all_animals_task = self.view.after(self.current_gui_time, self.view.board_frame.randomly_draw_all_animals)
            self.view.board_frame.scheduled_tasks.append(randomly_draw_all_animals_task)
            # adding delay
            buffer = int((self.model.total_populations[0] + self.model.total_populations[1])*3 + 500)
            self.current_gui_time += self.settings.random_pawn_placement_time + buffer # buffer

        # displaying the 'start round' button if the user has pause between rounds on
        if self.settings.pause_between_rounds == 'on': # autofinish is never on when pause between rounds is on
            # for autofinish game button
            self.view.after(self.current_gui_time, lambda command=self.start_round_button_command: setattr(self, 'next_game_command', command))
            # displaying the round start button
            display_start_round_button_task = self.view.after(self.current_gui_time, lambda:
                self.view.left_menu_frame.game_controls.start_round_button.grid(**self.view.left_menu_frame.game_controls.start_round_button_grid_info))
            self.view.board_frame.scheduled_tasks.append(display_start_round_button_task)
            # resetting gui time
            self.current_gui_time = 0
        # starts the round automatically if 'off'
        else:
            if self.settings.autofinish_game == 'off':
                self.current_gui_time += self.settings.delay_between_rounds * 1000 # adding customized buffer - in seconds
                start_round_button_command_task = self.view.after(self.current_gui_time, self.start_round_button_command)
                self.view.board_frame.scheduled_tasks.append(start_round_button_command_task)
                # for autofinish game button
                self.view.after(self.current_gui_time, lambda command=self.finish_round_button_command: setattr(self, 'next_game_command', command))
                self.current_gui_time = 500 # resetting gui time + buffer
            else:
                self.start_round_button_command()

    def start_round_button_command(self) -> None:
        """
        Handles events when the user clicks the Start Round button
        """
        if self.settings.autofinish_game == 'off':
            # hiding the start round button again
            start_round_button_hide_task = self.view.after(self.current_gui_time, self.view.left_menu_frame.game_controls.start_round_button.grid_forget)
            self.view.board_frame.scheduled_tasks.append(start_round_button_hide_task)
            # displaying countdown from 3 after gui has been fully updated with all animals
            display_game_countdown_task = self.view.after(self.current_gui_time,
                                        self.view.board_frame.display_game_countdown, 3)
            self.view.board_frame.scheduled_tasks.append(display_game_countdown_task)
            # adding to current gui time - GO label is 1250 milliseconds, 2000 is the buffer
            self.current_gui_time += (self.settings.delay_between_board_labels*2)//3 + int(self.settings.delay_between_board_labels*1.5) + 2000
        # calculating the results of the round
        self.model.modify_board_survivors()
        # assigning the resultant data to the board and square view objects
        self.controller.assign_models_to_views()
        # applying visuals
        if self.settings.autofinish_game == 'off':
            # displaying the rounds results feature
            diagonal_matrix_draw_all_results_task = self.view.board_frame.after(self.current_gui_time, self.view.board_frame.diagonal_matrix_draw_all_results)
            self.view.board_frame.scheduled_tasks.append(diagonal_matrix_draw_all_results_task)
            # adding to current gui time - multipying by the number of diagonal sections
            self.current_gui_time += self.settings.delay_between_square_results_labels*(2*self.settings.board_length-1)
            # updating the scoreboard
            update_scoreboard_task = self.view.after(self.current_gui_time, self.view.right_menu_frame.scoreboard.update_scoreboard)
            self.view.board_frame.scheduled_tasks.append(update_scoreboard_task)
            # adding buffer
            buffer = int(self.model.total_populations[0] + self.model.total_populations[1]*25 + 1000)
            self.current_gui_time += buffer
            # displaying the round winner
            display_round_winner_label_task = self.view.after(self.current_gui_time, self.view.board_frame.display_round_winner_label, self.model.round_winner)
            self.view.board_frame.scheduled_tasks.append(display_round_winner_label_task)
            self.current_gui_time += self.settings.delay_between_board_labels * 2 # used for winner label

        # displaying the 'finish round' button if the user has pause between rounds turned on
        if self.settings.pause_between_rounds == 'on': # autofinish is never on when pause_between_rounds is on
            self.current_gui_time += 1000 # adding buffer
            display_finish_round_button_task = self.view.after(self.current_gui_time, lambda:
                self.view.left_menu_frame.game_controls.finish_round_button.grid(**self.view.left_menu_frame.game_controls.finish_round_button_grid_info))
            self.view.board_frame.scheduled_tasks.append(display_finish_round_button_task)
            # for autofinish game button
            self.view.after(self.current_gui_time, lambda command=self.finish_round_button_command: setattr(self, 'next_game_command', command))
            self.current_gui_time = 0
        else:
            if self.settings.autofinish_game == 'off':
                # adding configured delay between rounds buffer - setting is 1 digit representing seconds
                self.current_gui_time += self.settings.delay_between_rounds * 1000
                finish_round_button_command_task = self.view.after(self.current_gui_time, self.finish_round_button_command)
                self.view.board_frame.scheduled_tasks.append(finish_round_button_command_task)
                # for autofinish game button
                self.view.after(self.current_gui_time, lambda command=self.scatter_pawns: setattr(self, 'next_game_command', command))
                self.current_gui_time = 500
            else:
                self.finish_round_button_command()
    
    def finish_round_button_command(self) -> None:
        """
        Handles events when the user clicks the Finish Round button
        """
        # hiding the finish round button
        if self.settings.autofinish_game == 'off':
            finish_round_button_hide_task = self.view.after(self.current_gui_time, self.view.left_menu_frame.game_controls.finish_round_button.grid_forget)
            self.view.board_frame.scheduled_tasks.append(finish_round_button_hide_task)
            # uncoloring the scoreboard's marker colors
            uncolor_scoreboard_text_task = self.view.after(self.current_gui_time, self.view.right_menu_frame.scoreboard.uncolor_scoreboard_text)
            self.view.board_frame.scheduled_tasks.append(uncolor_scoreboard_text_task)
            # displaying the collecting pawns label
            display_collecting_pawns_label_task = self.view.after(self.current_gui_time, self.view.board_frame.display_collecting_pawns_label)
            self.view.board_frame.scheduled_tasks.append(display_collecting_pawns_label_task)
            self.current_gui_time += self.settings.delay_between_board_labels + 1000 # buffer
            # collecting the board's pawns
            randomly_collect_all_animals_task = self.view.after(self.current_gui_time, self.view.board_frame.randomly_collect_all_animals)
            self.view.board_frame.scheduled_tasks.append(randomly_collect_all_animals_task)

        # recording the round's data
        model_helpers.record_round_data(
            (self.model.current_round, self.model.total_populations, self.model.average_levels, self.model.round_winner)
            )
        # adding delay
        buffer = int((self.model.total_populations[0] + self.model.total_populations[1])*15 + 500)
        self.current_gui_time += self.settings.random_pawn_placement_time + buffer
        # checking if it's the last round
        if self.model.current_round == self.settings.num_rounds:
            self.current_gui_time += 1000
            # finding and displaying the winner - team with highest net pop. change
            self.model.find_winner()
            if self.settings.autofinish_game == 'off':
                display_game_winner_label_task = self.view.after(self.current_gui_time, self.view.board_frame.display_game_winner_label, self.model.game_winner, 'show')
                self.view.board_frame.scheduled_tasks.append(display_game_winner_label_task)
            # finding and recording the start and end of game results
            model_helpers.record_start_and_end_data(self.initial_levels_to_populations, True)
            self.model.calculate_levels_to_populations()
            model_helpers.record_start_and_end_data(self.model.levels_to_populations, False)
            # writing this game's round_log to last_game_round_log
            model_helpers.transfer_round_logs()

            if self.settings.autofinish_game == 'off':
                # displaying export results button
                configure_export_button_task = self.view.after(self.current_gui_time, lambda: self.view.left_menu_frame.game_controls.export_data_button.config(
                    text='Export\nResults', style='highlighted_button.TButton')
                )
                self.view.board_frame.scheduled_tasks.append(configure_export_button_task)

                display_export_button_task = self.view.after(self.current_gui_time, lambda: self.view.left_menu_frame.game_controls.export_data_button.grid(
                    **self.view.left_menu_frame.game_controls.export_data_button_grid_info)
                    )
                self.view.board_frame.scheduled_tasks.append(display_export_button_task)
        else:
            # clearing the data from the model's previous squares and updating round number
            self.model.clear_board()
            # clearing all old scheduled tasks and labels - already over and done
            if self.settings.autofinish_game == 'off':
                self.view.after(self.current_gui_time, self.view.board_frame.scheduled_tasks.clear)
                self.view.after(self.current_gui_time, self.view.board_frame.scheduled_labels.clear)
                # scheduling next round
                scatter_pawns_task = self.view.after(self.current_gui_time, self.scatter_pawns)
                self.view.board_frame.scheduled_tasks.append(scatter_pawns_task)
                # for autofinish game button
                self.view.after(self.current_gui_time, lambda command=self.start_round_button_command: setattr(self, 'next_game_command', command))
                self.current_gui_time = 500
            else:
                self.scatter_pawns()



    def reset_game_button_command(self) -> None:
        """
        Handles events when the user clicks the Reset Game button
        """
        # deleting the old model    
        del self.model
        # cancelling upcoming visuals/labels
        self.cancel_all_tasks_and_visuals()
        # resetting the scoreboard
        self.view.right_menu_frame.scoreboard.reset_scoreboard_text()
        # unlocking the user's configuration settings
        self.change_configuration_widget_states('normal')
        # only showing the start game button
        self.change_game_buttons_shown('reset')
        # if the export button exists, changing it's text - now the last game's results
        self.view.left_menu_frame.game_controls.export_data_button.config(text='Export  Last\n    Results', style='TButton')

    def autofinish_game_button_command(self) -> None:
        """
        Handles events when the user clicks the Autofinish Game button -
        main-game loop completes all calculations for the game, then this method cancels the visuals,
        displays the winner, updates scoreboard, and displays certain buttons
        """
        previous_pause_between_rounds = self.settings.pause_between_rounds
        self.settings.update_settings(('change_of_rounds', 'pause_between_rounds', 'off'))
        self.settings.update_settings(('change_of_rounds', 'autofinish_game', 'on'))
        # cancelling upcoming visuals/labels - clears the board
        self.cancel_all_tasks_and_visuals()
        # conducting the calculations for every round without the visuals from where game mainloop left off
        self.next_game_command()
        # changing the text of the export data button
        self.game_controls_frame.export_data_button.config(text='Export\nResults', style='highlighted_button.TButton')
        # showing only reset game and export data buttons
        self.change_game_buttons_shown('autofinish')
        # displaying the game winner label
        self.view.board_frame.display_game_winner_label(self.model.game_winner, 'show')
        # updating then uncoloring the scoreboard text
        self.view.right_menu_frame.scoreboard.update_scoreboard()
        self.view.right_menu_frame.scoreboard.round_label.config(text=f'Round {self.settings.num_rounds}')
        self.view.right_menu_frame.scoreboard.uncolor_scoreboard_text()
        # reconfiguring the user's settings to their original
        self.settings.update_settings(('change_of_rounds', 'pause_between_rounds', previous_pause_between_rounds))
        self.settings.update_settings(('change_of_rounds', 'autofinish_game', 'off'))

    def export_data_to_excel_button_command(self) -> None:
        """
        Handles events when the user clicks the Export Game Data to Excel button
        """
        model_helpers.export_game_data_to_excel()
    
    def cancel_all_tasks_and_visuals(self) -> None:
        """
        Cancels all the scheduled tasks and destroys all labels on the screen
        needed to immediately stop the visuals for the reset and autofinish game buttons
        """
        # canceling all active visual tasks
        while self.view.board_frame.scheduled_tasks:
            task = self.view.board_frame.scheduled_tasks.pop()
            self.view.board_frame.after_cancel(task)
        # removing any existent labels
        for label in self.view.board_frame.scheduled_labels:
            if label.winfo_exists():
                label.destroy()
        self.view.board_frame.scheduled_labels.clear()

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
            - button_press (str): the button clicked - accepts
                - 'start' : hides and shows certain buttons when the 'start game' button is pressed
                - 'reset' : hides and shows certain buttons when the 'reset game' button is pressed
                - 'autofinish' : hides and shows certain buttons when the 'autofinish game' button is pressed
        """
        if button_press == 'start':
            self.game_controls_frame.start_game_button.grid_forget()
            self.game_controls_frame.placeholder_label.grid_forget()

            self.game_controls_frame.reset_game_button.grid(
                **self.game_controls_frame.reset_game_button_grid_info)
            self.game_controls_frame.autofinish_game_button.grid(
                **self.game_controls_frame.autofinish_game_button_grid_info)
        
        elif button_press == 'reset':
            self.game_controls_frame.start_game_button.grid(
                **self.game_controls_frame.start_game_button_grid_info)
            self.game_controls_frame.placeholder_label.grid(
                **self.game_controls_frame.placeholder_label_grid_info)

            self.game_controls_frame.reset_game_button.grid_forget()
            self.game_controls_frame.autofinish_game_button.grid_forget()
            self.game_controls_frame.start_round_button.grid_forget()
            self.game_controls_frame.finish_round_button.grid_forget()
        
        elif button_press == 'autofinish':
            self.game_controls_frame.export_data_button.grid(
                **self.game_controls_frame.export_data_button_grid_info)
            self.game_controls_frame.placeholder_label.grid(
                **self.game_controls_frame.placeholder_label_grid_info)

            self.game_controls_frame.autofinish_game_button.grid_forget()
            self.game_controls_frame.start_round_button.grid_forget()
            self.game_controls_frame.finish_round_button.grid_forget()
            
        else:
            raise ValueError("The button_press argument must either be 'start' or 'reset'")

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
            self.settings.update_settings(('change_of_rounds', 'pause_between_rounds', 'on'))
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
            # updating scales and scale markers to their default set points and max
            self.predator_population_scale_command(self.default_settings['predator']['num_initial_predators'])
            self.configurations_frame.custom_predator_population_scale.set(self.settings.num_initial_predators)
            self.configurations_frame.custom_predator_population_scale.configure(to=(self.settings.board_length**2)*4)

            self.predator_level_scale_command(self.default_settings['predator']['predator_starting_level'])
            self.configurations_frame.custom_predator_level_scale.set(self.settings.predator_starting_level)

            self.predator_starvation_scale_command(self.default_settings['predator']['rounds_until_starvation'])
            self.configurations_frame.custom_predator_starvation_scale.set(self.settings.rounds_until_starvation)

            self.prey_population_scale_command(self.default_settings['prey']['num_initial_prey'])
            self.configurations_frame.custom_prey_population_scale.set(self.settings.num_initial_prey)
            self.configurations_frame.custom_prey_population_scale.configure(to=(self.settings.board_length**2)*4)

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