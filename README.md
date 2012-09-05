Total Annihilation
=================

A game server for a digital robotic war - an open warzone where robots come to have fun.

Total Annihilation is a timed turn based programming challenge game where players design and implement their own robots and have them battle other player's implementations online.
The goal is to deal as much damage to other robots while trying to stay alive in the fierce environment.

Initial design
--------------

 - The server executes a turn at a fixed interval.
 - Clients need to send orders to their robot before the next interval (putting a time contraint on the algorithm complexity).
 - Clients are allowed to *fire*, *move* and *scan* once every turn (the actions being executed in that order server side).
 - Clients have a particular amount of energy, being used to fire, move and scan and doubles as a life total.
 - The energy cost of both moving and scanning is solely based on the distance / range the action is performed.
 - The energy cost of firing is based on the distance and the desired blast radius of the 'bullet'.
 - A robot reaching 0.0 energy dies, either through 'exhausing' itself or being hit.
 - Points are earned by hitting a robot in the turn that it dies (the exact score for a combination of hitting an opponent and it exhausting itself to be determined later).

(more to follow)
