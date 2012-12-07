from process import Process

class Simulator:
    def __init__(self, rounds, num_proc):
        self.rounds = rounds
        self.processes = []
        
        for i in range(0, num_proc):
            self.processes.append(Process(i, num_proc))
            
    
    def simulate(self, mode):
        """simulates sending of msgs. Mode can be 'latency', 'throughput'"""
        if mode == 'latency':
            self._simulate_latency_1_sender()
        elif mode == 'throughput':
            self._simulate_throughput()
    
    def _simulate_latency_1_sender(self):
        for turn in range(0,self.rounds):
            #Start the sending of messages (puts messages in outbox)
            if turn % 1 == 0: #Trivial, just to make it consistent with other simulations
                self.processes[0].broadcast("Multicast")
                
            self._dist_round_msgs()
            self._print_turn(turn)
            
        
    def _dist_round_msgs(self):
        for proc in self.processes:
                if proc.outbox:
                    dest = proc.outbox[0][1]
                    if dest and not self.processes[dest].received:
                        self.processes[dest].received = proc.outbox.pop()
                    elif not dest: #Broadcast in Multicast
                        msg = proc.outbox.pop()
                        for p in self.processes:
                            if p != proc:
                                p.received = msg
                    else: #There was a collision (should not happen). Has a dest and dest has received a message this round
                        print "Collision detected when sending from " + proc.pid + " to " + dest.pid + ". Destination already had already received message " + dest.received


    def _print_turn(self, turn):
        """Print a nice output to follow the sending of messages each round"""
        
        print "Turn: " + str(turn)
        print "<PID>" + "\t" + "Message Received (Sender, Type)"
        for i in self.processes:
            print str(i.pid) + "\t" + str(i.received)        
        print ""

sim = Simulator(3, 4)
sim.simulate('latency')
