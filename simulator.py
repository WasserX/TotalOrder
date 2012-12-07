from process import Process

class Simulator:
    def __init__(self, rounds, num_proc):
        self.rounds = rounds
        self.round = 0
        self.processes = []
        
        for i in range(0, num_proc):
            self.processes.append(Process(i, num_proc))
            
    def simulate(self):
        self.processes[0].broadcast()
        
        while self.round < self.rounds:
        
            for proc in self.processes:
                if proc.outbox:
                    dest = proc.outbox[0][1]
                    if dest and not self.processes[dest].received:
                        self.processes[dest].received = proc.outbox.pop()
                    else:
                        msg = proc.outbox.pop()
                        for p in self.processes:
                            if p != proc:
                                p.received = msg
                    
            
            for i in self.processes:
                print i, i.received
            
            self.round += 1    
        
        
        return 0

#Can delete, just to test...
        #try:
        #    rounds=int(raw_input('Number of rounds to simulate:'))
        #except ValueError:
        #    print "Not a valid number of rounds"
        
        
simulator = Simulator(1, 5)
simulator.simulate()        
