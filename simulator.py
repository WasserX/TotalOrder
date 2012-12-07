from process import Process

class Simulator:
    def __init__(self, rounds, num_proc):
        self.rounds = rounds
        self.processes = []
        
        for i in range(0, num_proc):
            self.processes.append(Process(i, num_proc))
            
    
    def simulate(self, mode):
        """simulates sending of msgs. Mode can be 'latency', 'throughput'"""
        if mode == 'latency 1':
            self._sim_latency_1_1sender()
        elif mode == 'latency 3':
            self._sim_latency_3_1sender()
        elif mode == 'pipeline':
            self._sim_pipeline()
        elif mode == 'throughput':
            self._sim_throughput()
    
    def _sim_latency_1_1sender(self):
        for turn in range(0,self.rounds):
            #Process msgs received in previous round
            for proc in self.processes:
                proc.receive()
            
            #Put new data msgs in outbox
            if turn % 1 == 0: #Latency for one msg
                self.processes[0].broadcast("Multicast")
                
            self._dist_round_msgs()
            self._print_turn(turn)
            
            
    def _sim_latency_3_1sender(self):
        for turn in range(0,self.rounds):
            #Process msgs received in previous round
            for proc in self.processes:
                proc.receive()
        
            #Put new data msgs in outbox
            if turn % 3 == 0: #Latency for one msg
                self.processes[0].broadcast("Unicast")
             
            self._dist_round_msgs()
            self._print_turn(turn)
            
    def _sim_pipeline(self):
        for turn in range(0,self.rounds):
            #Process msgs received in previous round
            for proc in self.processes:
                proc.receive()
        
            #Put new data msgs in outbox
            #In this case we use a circular list to send each round
            if turn % 3 == 0: #Latency for one msg
                for proc in self.processes[:-1]:
                    proc.broadcast("Unicast", range(proc.pid+1, len(self.processes)) + range(0, proc.pid))
             
            self._dist_round_msgs()
            self._print_turn(turn)
            
        
    def _dist_round_msgs(self):
        for proc in self.processes:
            if proc.outbox:
                dest, msg = proc.outbox.pop()
                if dest == None: #Broadcast in Multicast
                    for p in self.processes:
                        p.received = msg
                elif dest != None and not self.processes[dest].received:
                    self.processes[dest].received = msg
                else: #There was a collision (should not happen). Dest has received a message this round
                    print "Collision detected from " + str(proc.pid) + " to " + str(dest) + ". Destination already has " + str(self.processes[dest].received)


    def _print_turn(self, turn):
        """Print a nice output to follow the sending of messages each round"""
        
        print "Turn: " + str(turn)
        print "<PID>" + "\t" + "Message Received (Sender, MSGID, Type)"
        for i in self.processes:
            print str(i.pid) + "\t" + str(i.received)        
        print ""

sim = Simulator(3, 4)
sim.simulate('pipeline')
