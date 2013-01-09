TotalOrder
==========

Total Order Message Sending Simulator for the Distributed System Course

Instructions:
Uses Python 2.7

To execute create a settings file in the format:
<BCTREE|BCUNI|BCPIPE|TOLAT|TOTHROUGH>
<number of processes to simulate>
[turn pid]
...
[turn pid]


BCTREE => Simulate a broadcast using a tree algorithm to distribute
BCUNI =>  Basic broadcast where the original sender sends to all recipients
BCPIPE => Broadcast where the sender only sends to the next one, and so on.
TOLAT =>  Total Order Broadcast optimized to reduce latency
TOTHROUGH => Total Order Broadcast optimized to increase throughput
 
(turn, pid) is a pair where turn specifies the round where pid will try to start sending a new message
