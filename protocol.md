Network connection life cycle
=============================

Communication with a LoBotomy server is done by opening a network socket to it and starting a conversation.
To keep things simple, such a conversation is done by sending strings over the network connection.
A single command consists of the command's name and its arguments separated by spaces, terminated with a newline character (`\n`).
So, for example, a command the client might use to tell the server it wants to join the game, the client might execute the following code:

```java
// define our name to be Henk
String name = 'Henk';
// write the join command, followed by a space and our name, terminated with a newline
output.write('join' + ' ' + name + '\n');
```

As we model client/server communication as a conversation, the server could respond with a welcome message, read by the client as such:

```java
// read a line from our input
String line = input.readLine();
// parse the line into a command and arguments
String[] parts = line.split(" ");
// handle the command
if (parts[0].equals("welcome")) {
	handleWelcome(parts);
}
```

The above might not be the most efficient code, but the idea is clear.

Protocol
--------

The conversation between client and server supports the following commands:

### join
Format: `join name`

Sent by the client to request to join the game using a particular name (containing just alphanumeric characters).

### welcome
Format: `welcome version energy turn-duration turns-left`

Sent by the server to welcome a player to the game and provide some game settings:

1. **version** (integer): the protocol version used by the server;
1. **energy** (float): the starting and maximum energy for players;
1. **turn-duration** (integer): the number of milliseconds a turn will take;
1. **turns-left** (integer): the number of turns the current game has left (or -1 if the game is run perpetual).

### spawn
Format: `spawn`

Sent by the client to request to be put on the battlefield in the next turn.

### begin
Format: `begin turn-number energy`

Sent by the sever to indicate the start of a new round. Arguments inform a player of:

1. **turn-number** (integer): an incremental identifier for the current turn;
1. **energy** (float): the amount of energy the player currently has.

### move
Format: `move angle distance`

Sent by the client to request a move action to be performed in the current turn with the following details:

1. **angle** (radian, float): the direction in which to move;
1. **distance** (float): the distance to move.

### fire
Format: `fire angle distance radius yield`

Sent by the client to request a fire action to be performed in the current turn with the following details:

1. **angle** (radian, float): the direction in which to fire a bomb;
1. **distance** (float): the distance to fire the bomb;
1. **radius** (float): the radius of the bomb's explosion;
1. **yield** (float): the energy dissipation of the bomb (amount of damage).

### scan
Format: `scan radius`

Sent by the client to request a scan action to be performed in the current turn with the following details:

1. **radius** (float): the radius of the scan, centered on the player.

### end
Format: `end`

Sent by the server to indicate that no further actions will be accepted before for the current turn and it will execute the current turn.

### hit
Format: `hit name angle yield`

Sent by the server to indicate that a player was hit by a bomb, with the following details:

1. **name** (string): the name of the player that fired the bomb;
1. **angle** (radian, float): the direction the blast came from (the epicenter of the blast);
1. **yield** (float): the strength of the bomb.

### death
Format: `death turns`

Sent by the server to inform a player that they are dead and how long the need to wait before they can respawn:

1. **turns** (integer): how long the player will stay dead.

### detect
Format: `detect name angle distance energy`

Sent by the server to inform a player that their scan detected another player, with the following details:

1. **name** (string): the name of the detected player;
1. **angle** (radian, float): the direction of the detected player;
1. **distance** (float): the distance of the detected player;
1. **energy** (float): the amount of energy of the detected player.

### error
Format: `error error-code explanation`

Sent by the server in response to a command sent by the client to indicate that the command could not be accepted, with the following details:

1. **error-code** (integer): numerical representation of the error;
1. **explanation** (string): an elaboration of the error, only serving a debug purpose (not to be used by clients in any meaningful way).

