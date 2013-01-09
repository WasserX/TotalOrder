from process import *
import random

class Simulator:
    def __init__(self):
        self.nproc = 0

    def simulate(self, mode, nproc):
        """Simulates a broadcast or a Total Order Broadcast. Available modes are
        'BCUNI', 'BCTREE', 'BCPIPE', 'TOLAT', 'TOTHROUGH'. 
        nproc defines the number of processes in the simulation"""
        
        self.nproc = nproc
        self.processes = []
        self.send_queue = []
        
        if mode == 'BCUNI':
            for i in range(0, self.nproc):
               self.processes.append(Process(i, self.processes, self.send_queue))
            self.sim_broadcast()
        elif mode == 'BCTREE':
            sending_order = []
            for i in range(0, self.nproc):
                self.processes.append(TreeProcess(i, self.processes, self.send_queue, sending_order))
            self.sim_broadcast()
        elif mode == 'BCPIPE':
            for i in range(0, self.nproc):
                self.processes.append(PipeProcess(i, self.processes, self.send_queue))
            self.sim_broadcast()
        else:
            print 'Mode not recognized'
    
    def deliver_msgs(self, mode):
        """Simulates the msg transfer. Essentially puts the msg of the sender in the destination."""
        for sender, to, msg in self.send_queue:
            to.to_receive.append(msg)
            
        del self.send_queue[:]


    def sim_broadcast(self):
        """Broadcasts a msg without acks using the processes algorithm to spread"""

        #Sender of the packet
        senders = [[random.randrange(self.nproc), 0]]
        self.processes[senders[0][0]].send_new = True #Set flag to tell sender to create new msg
        
        #Execute rounds
        turn = 0
        working = True
        while working:
            turn = turn +1
            print '-- Round ' + str(turn) + ' --'

            for proc in self.processes:
                #Execute round for each process
                proc.do_round()

            #Deliver msgs for next round
            self.deliver_msgs('UNICAST')

            #Check if needs to continue executing
            working = False
            for proc in self.processes:
                working = True if proc.to_send or proc.to_receive else working
                
            if working:
                #Increase latencies
                for sender in senders:
                    sender[1] = sender[1] + 1

        latency = -1
        for sender in senders:
            latency = sender[1] if latency < sender[1] else latency

        self.print_results(self.nproc, turn-1, latency, (len(senders), turn-1))


    def print_results(self, nproc, rounds, latency, throughput):
        print '-- Simulation Ended --'
        print 'Results:'
        print '    Nb of Processes: ' + str(nproc)
        print '    Rounds: ' + str(rounds)
        print '    Latency: ' + str(latency)
        print '    Throughput: ' + str(throughput[0]) + '/' + str(throughput[1])

test = Simulator()
test.simulate('BCTREE', 4)
