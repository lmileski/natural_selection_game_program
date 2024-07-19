# Evolving Battles: Predators vs. Prey

## A customizable GUI board game written in Python that simulates trends in natural selection.

<img src="natural_selection_program_picture.png" width=900 height=500>

## Overview

This project automates University of San Diego's EOSC 123 natural selection lab. The intention of this application is to supplement the lab by allowing students to efficiently test their claims on natural selection. In addition to the substantial reduction in time constraint, this program also eliminates the likelihood of human error, allows for customizations, and automatically generates excel tables holding the completed game's data.

## Useful Links

* [rulebook](https://onedrive.live.com/edit.aspx?resid=3d8c06f048f6c577!3629)
* [installation_demo_video](https://youtu.be/bOwVrPre-oM?si=Spf6fwqrfpR1AqF1)
* [simulation_demo_video](https://youtu.be/3AdRpmGF3ns?si=M4Y0PAbKl4fT4gmG)
* [leave_a_review](https://docs.google.com/forms/d/e/1FAIpQLSduCBih2TzSOCG_rc5sQ_SZZrGLK6um6K9d3Sa8OO_rdWQ7LQ/viewform)

**Note:**
The installation video is designed for Windows computers.
If you have a Windows computer, use that. However, if you must use Mac or Linux,
extra installation steps are required due to incompatibilities. You must complete all
steps mentioned in my installation demo video then either:
1) Download Wine and use that to run the .exe file from my code provided

* Video on how to do so for Mac: https://www.youtube.com/watch?v=Bz-nI4LW2Jw&t=0s
* Video on how to do so for Linux: https://www.youtube.com/watch?v=TatVttlvo2A&t=0s

2) Or run the controller.py file from my provided code in your own terminal

* This option is less recommended
* It requires you to also install all modules used in my code.
* May be more complicated for non-coders

Also please leave a review using the above link. It helps a ton!

## GUI Layout

* A Title panel with game credits and links to my github, the game details, and a review of this program
* A Board Grid panel displaying the current predator/prey pawns and all changes between rounds
* A Game Controls panel with the following widgets:
    * Start/Reset Game button
    * Start/Finish Round button
    * Autofinish Game button
    * Export Results button (opens an excel file preloaded with the last completed game's data)
    * Number of Rounds scale
* A Customize Settings panel with the following widgets:
    * Customize Board checkbutton (for configuring the board size and colors)
    * Automatic Round Start checkbutton (conducts game without the need for user interaction)
    * Customize Starting Animals checkbutton (for configuring the inital predator/prey pawn populations, skill levels, and satiety levels)
    * Restore Default Settings button (unchecks all checkbuttons and removes user's settings changes)
* A Scoreboard panel holding the current round and predator/prey pawn stats (population, skill level, and sateity level)
* A Board Key panel describing the predator/prey pawn visuals and result symbols

## Code Synopsis

The natural selection simulation is built fully in python and utilizes the tkinter library for the GUI. I organized the code using the MVC architecture by creating separate files for the model, view, and controller. Supplementary functions related to the model such as file writing, recording data, and game logic were placed is model_helpers.py. All data required for the completion of the lab is recorded throughout the game in various .csv files found under the game_results_logs folder. The default and user-configured settings to be modified throughout the game are stored as .json files under the game_settings_logs. Lastly, either start_program_here.exe or controller.py can be run to start the simulation, but only from their relevant placement within the folder.

## Rundown of File Contents

### view.py

### model.py

### controller.py