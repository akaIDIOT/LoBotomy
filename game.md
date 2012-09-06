Game design
===========

A player is a robot on a square battlefield that wraps on all edges.
The size of the battlefield is defined as being 2 distance units wide and 2 distance units high.
All locations and action definitions are provided relative to the player in question, so exact locations on a 'grid' are out of scope.

A player is capable of three things: moving about, firing a bomb and scanning around them.
Everything a player does costs a certain amount of energy.
Moving 0.2 distance units at a 90° angle might cost 0.2 energy units.
Similarly, scanning around for a radius of 0.4 distance units might cost 0.4² = 0.16 energy units (the actual costs will be determined later, but you get the gist).

As everything costs energy, a player has a certain amount of it.
If energy runs out (by moving too far or getting shot at, for example), a player dies.
Luckily, robots obviously have solar panels and battlefields are like perpetual summer, so players get a fixed amount of energy per turn.
The details on firing a bombs and the energy cost of firing distance, bomb yield and blast radius combined with how much hurt a bomb causes are yet to be determined.

Turn cycle
----------
A turn starts out with a broadcast to all players that the next turn starts.
At this point, all players can determine their next actions and send these to the server.
The server keeps all valid requests until the turn time has expired, at which point all actions are performed at the same time for all players.
A turn has three steps, in order:

 - **Moving**: all requested moves are done.
 - **Firing**: all requested bombs are fired.
 - **Scanning**: all requested scans are made.

Note that as moves are done before bombs, some guess as to the location of an adversary will have to made.

Results for actions are transmitted back to clients, after which a new turn is broadcast and the cycle starts again.

How a player can be reincarnated, how scores are calculated and the like are all unknown at the moment.
Gaps will be filled when there is a clear moment for it to be filled :)
