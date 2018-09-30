# EgyptianRatScrew
The card game Egyptian Rat Screw built to be played by multiple players from terminal.

# Rules
sdfsfsd

Slapping always overwrites face or ace card. So if player 1 would win the round because of an ace that he played 
a round ago but then he accidently slaps the pile he will lose 2 cards as penalty and the game will continue.


# Tools
serpent instead of pickle

# Run instructions ()

## start up the nameserver (Only 1 person needs to do this)
python -m Pyro4.naming

## start the game server (One 1 person needs to do this)
python server.py

## start the client (Each player needs to do this)
python client.py

# Design Choices
In terms of modularity, this code is not really 

# Future 
In the future I would want to think a lot more about scalability. The star network topology
here would just be awful. The game server stores all the information
Deal with disconnections


# Future Functionality to Add
Add lobbies, difficulty levels, handle disconnects

# design choices:
- allowing a player to decide when to turn their card or automating it
 --> ultimately decided to automate the card flipping although I originally kept it 
 	because it slowed down the flow of the game a lot waiting for a player to flip a card 