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

### welcome
Format: `welcome version energy turn-duration turns-left`

### spawn
Format: `spawn`

### turn
Format: `turn turn-number energy`

### move
Format: `move angle distance`

### fire
Format: `fire angle distance radius yield`

### scan
Format: `scan radius`

### ok
Format: `ok`

### hit
Format: `hit name angle yield`

### death
Format: `death turns`

### detect
Format: `detect name angle distance energy`

### error
Format: `error error-number explanation`

