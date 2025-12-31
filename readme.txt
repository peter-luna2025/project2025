1Card Poker (Pygame) - README
============================

1. Overview
-----------
This is a simple basic game application for a 1Card Poker card game. It can be played by 2, 3, or 4 players using a deck of 52 cards. 
The objective of the game is to get the highest rank of card drawn from the deck to win the round. At the start of the game, each player will receive 1 card from the dealer and the app will automatically analyze the card and determine the winner.

It uses:
- Python 3
- Pygame for the GUI

Features:
- Simulates the dealing of the cards and deals with deck 	management
- Player setting and token handling
- Scoring and winner determination
- Visual representation of cards using images or text
- Gui layout
	player buttons and tokens
	buttons for player selections, start action, next round, 	adding player names

2. Running from source
----------------------
Requirements:
- Python 3.10 or newer
- Pygame (bundled with standard Python on Windows)
- No extra packages required

Steps:
1. Open a terminal in the "project_2025" folder.
2. Run:
   python project.py

3. Assets
---------
the following files in the "project_2025/assets" folder:

- cards   (card images from Ace to King)
- sounds  (3 actions: card dealing, winner announcement and card 		shuffling music can be incorporated))
The paths and names of the files:
project_2025/project.py, requirement.txt and README.txt
project_2025/assets/
		 /cards

Starting the game:
From CLI, type:  python project.py
	The game will open a menu screen where you can see the 	structure of the game.

	Steps on how to start the game.

	1. user pick one of the players options shown on the menu.
	2. click add names: to add names of the players
	3. press start game button, to start
	4. the program will show the flow of the game
	5. the program will automatically show the tokens in the middle of the table
	6. program will deal each player 1 card automatically
	7. program will evaluate the cards and determine the winning player of that round.
	8. if user want to go the next round, a next round button is available.

	Here is the location of my video:

	1Card-Poker
	Video Demo: <https://youtu.be/ZyuJYGIEV5o
	description: project2025
	








