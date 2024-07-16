# Evolving Battles: Predators vs. Prey

## A customizable GUI board game written in Python that simulates trends in natural selection.

<img src="natural_selection_program_picture.png" width=900 height=600>


This project automates University of San Diego's EOSC 123 natural selection lab. The intention of this application is to supplement the lab by allowing students to efficiently test their claims on natural selection. In addition to the substantial reduction in time constraint, this program also eliminates the likelihood of human error, allows for customizations, and automatically generates excel tables holding the completed game's data.

The following is a list of components in this application's GUI layout:

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


## Watch a demo on how to use the application!

https://youtu.be/3AdRpmGF3ns?si=M4Y0PAbKl4fT4gmG

## Watch a demo on installation!

https://youtu.be/bOwVrPre-oM?si=Spf6fwqrfpR1AqF1

**Note:**
The installation video is designed for Windows computers.
If you have a Windows computer, use that. However, if you must use Mac or Linux,
extra installation steps are required due to incompatibilities. You must either:
1) Download Wine and use that to run the .exe file from my code provided

* Video on how to do so for Mac: https://www.youtube.com/watch?v=Bz-nI4LW2Jw&t=0s
* Video on how to do so for Linux: https://www.youtube.com/watch?v=TatVttlvo2A&t=0s

2) Run the controller.py file from my provided code in your own terminal

* This option is less recommended
* It requires you to also install all modules used in my code.
* May be more complicated for non-coders