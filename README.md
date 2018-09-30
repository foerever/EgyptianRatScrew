# EgyptianRatScrew
The card game Egyptian Rat Screw built to be played by multiple players from terminal.

# Rules


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
Scalability is not really an issue here. If we worried about that I would definitely be 


# Future 
In the future I would want to think a lot more about scalability. The star network topology
here would just be awful. The game server stores all the information
Deal with disconnections


# Future Functionality to Add
Add lobbies, difficulty levels