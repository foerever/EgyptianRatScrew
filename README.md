# Console Based Egyptian Rat Screw
This is a console based version of the card game Egyptian Rat Screw. Multiple people can play this game at a time. 

Build by Sung Soo (Anthony) Cho :) You can learn more about me at http://anthonycho.net/.

# Rules
I've based the rules for this game on Bicycle's website:
https://www.bicyclecards.com/how-to-play/egyptian-rat-screw/

## Objective
The objective of the game is to get all the cards that are in play.

## Playing 
The deck should be shuffled and then equally distributed amongst the players. This is handled automatically by the game.

Players pull the top card off their pile and place it in a pile in the middle such that all the other players can see it equally well at the same time. The game also takes care of this.

If a face card or ace is played, the next person in the sequence must play another face or ace card. The last person to play a face or ace card wins the round. Winning a round means you get the main pile of cards in the middle. In our game we automatically shuffle a player's cards upon merging any new gains. 

A successful slap overrides a face or ace. Reference the slap rules below, but the first valid slap on the main pile will make that player the winner of the round. This is a game of speed but be careful, if you slap incorrectly up to two cards (as many as possible but only up to two) will be taken from your deck and put at the bottom of the main pile. 

A player does not lose upon losing all of their cards and any such players can continue to play by slapping. Since such players obviously have no cards to play upon their turn, the player next in sequence will play their card instead. 

The only end condition to this game is when a single player has all the cards that the game started with.

## Slap Conditions
- Double: two consecutive cards of equivalent value (EX: 2, 2) 
- Sandwich: two consecutive cards of equivalent value with a card of different value between them (EX: 2, 3, 2)
- Top Bottom: when the top card is the same as the bottom in the main pile (EX: 1, 2, 4, King, 2, 5, 1)
- Four in a row: when four consecutive cards are in ascending or descending order (EX: 10, Jack, Queen, King but not contiguous so this is not four in a row: King, 2, 3, 4)

## Prequisites
There needs to be at least 2 players to play this game and a standard 52-card deck without jokers.

# Design 
I treated this challenge question like an actual software project I would work on. The timeline I set for myself was around 3-5 hours. 

## High Level Overview
I run a nameserver and server. Any user can connect to this network (the game) and interact with the game state through the client. The client polls the server for updates and only interacts with other clients through the server. The server holds a deck which in turn contains cards which are distributed at the beginning of the game. These cards can be put into deques which we call piles. Each user has a pile (the user's cards) and ready state. The ready state is important because it's how the server directs the game forward and each user needs to be engaged for the game to move slowly as the server will wait on every user to respond to each round. 

## Gameplay
I wanted the game to be as simple as possible. Growing up ERS was one of those stupid simple games to play, you just try to slap combos as fast as possible and that's exactly what I wanted to get across here as well. I automated certain parts of the game such as flipping and figuring out who slapped first so that the gameplay could be a lot smoother. The flow of the game is very linear. You connect to the server and you are immediately prompted for your name. In the game, your name must be unique. When you are in the "lobby" you essentially just get to choose whether you are ready to start the game, check whether other players are ready, or quit. Once all players in the lobby are in agreement to begin, the game begins. Once the game begins, each player will be given the choice of slapping or not, once the decision is made the players will receive an update about who won the round. It's important to slap as soon and as accurately as possible. The server receives "slaps" as a tuple of name and timestamp with millisecond resolution. The first correct slapper will take the round and so on and so forth (as according to the game rules). The game ends when a player has the maximum count of cards.

## Network Topology
I knew that in the timeline I set for myself I couldn't be too picky about network topology. I would have preferred it if I could have abstracted my components a lot more and allowed for both star and pier to pier. I ended up deciding on star network because although technically we could have some n number of players at a time all heavily relying on the server for coordinating and maintaining the game state, scaling for that wasn't realistically in scope nor is it realistic to expect a game of ERS to have some large n number of players. It was also the simplest topology to implement especially since it was my first time using Python/Pyro4 to build software applications.

## General Object Oriented Design
My OOP design here is kind of regretful. It's okay for this particular game, having an object for a deck which holds card objects, abstracting server and client, maintaining the game state only in the server, etc. These are fairly straightforward decisions for a relatively simple game. However, I wish that I had abstracted my components a lot more. Preferably I would be able to build on this system quite easily, adding lobbies or new random rules. The idea is that the system would be built more like a enterprise platform than it is just a simple game because long term it's a lot easier to maintain, scale, and build on. Right now I have this big monolithic server that basically handles everything. Again, given the scope it works but if this was a longer term project I was undertaking I definitely would not simplify the design this much.

## Tools
**Python 3.6.3** 
I used Python because I've actually done a very similar project before but for messaging using Java and wanted to learn something new. I think because of the scope of the project I wasn't too picky about what language I chose but I did want to chose a language I knew I could iterate quickly with. I talk about decisions I would make differently in my design section. One thing I didn't expect was that, when building actual software products, I actually prefer statically typed languages. I typically only use python for more statistical, scripting, or algorithmic purposes so development of this card game at first was a bit slow.

**Pyro4**
This is a Python library for using objects that can interact with each other remotely. I've never used this library before but I skimmed through their documentation and recognized a lot of main concepts they implement from working with Java RMI so I went ahead with it. 

## Testing
I did not standarize a lot of the testing I did but I've included a very brief coverage test that can be run by going to the src directory and using the command "python coverage.py". I definitely should have made sure I had at least 80% coverage and some more flexible testing. 


# Running Instructions
You can test it by yourself by just opening a new terminal for each one of these tasks. Before you begin you'll need to have installed Pyro4 and Python. Assuming you have Python and Pip you can install Pyro4 by the command "pip install Pyro4". Also all participants should be on the same network.

Open a terminal in the src directory and enter the following in this order:

### start up the nameserver (Only 1 person needs to do this)
python -m Pyro4.naming

### start the game server (One 1 person needs to do this)
python server.py

### start the client (Each player needs to do this)
python start.py

### kill the server/nameserver/client
control c 