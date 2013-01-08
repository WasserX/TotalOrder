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

        if mode == 'BCUNI':
            self.sim_bcuni()
        elif mode == 'BCTREE':
            self.sim_bctree()
        elif mode == 'BCPIPE':
            self.sim_bcpipe()
        else:
            print 'Mode not recognized'
    
    def deliver_msgs(self, processes, mode):
        """Simulates the msg transfer. If there is a collision a error will be
        reported. Essentially puts the msg of the sender in the destination."""
        for proc in processes:
            if proc.sent_msg:
                if proc.sent_msg[0].rcvd_msg:
                    print 'Collision, Aborting'
                    return
                else:
                    proc.sent_msg[0].rcvd_msg = proc.sent_msg[1]
                    proc.sent_msg = None


    def sim_bcuni(self):
        """Broadcasts a msg using unicast to all participants."""
        processes = []
        for i in range(0, self.nproc):
            processes.append(Process(i, processes))

        #Sender of the packet
        senders = [[random.randrange(self.nproc), 0]]
        processes[senders[0][0]].send_new = True
        
        #Execute rounds
        turn = 0
        working = True
        while working:
            turn = turn +1
            print '-- Round ' + str(turn) + ' --'

            for proc in processes:
                #Execute round for each process
                proc.do_round()

            #Deliver msgs for next round
            self.deliver_msgs(processes, 'UNICAST')

            #Check if needs to continue executing
            working = False
            for proc in processes:
                working = True if proc.sent_msg or proc.rcvd_msg else working
                
            if working:
                #Increase latencies
                for sender in senders:
                    sender[1] = sender[1] + 1

        latency = -1
        for sender in senders:
            latency = sender[1] if latency < sender[1] else latency

        self.print_results(self.nproc, turn-1, latency, (len(senders), turn-1))


    def sim_bctree(self):
        """Broadcasts a msg using unicast with tree algorithm."""
        processes = []
        delivery_order = []
        for i in range(0, self.nproc):
            processes.append(TreeProcess(i, processes, delivery_order))

        #Sender of the packet
        senders = [[random.randrange(self.nproc), 0]]
        processes[senders[0][0]].send_new = True
        
        #Execute rounds
        turn = 0
        working = True
        while working:
            turn = turn +1
            print '-- Round ' + str(turn) + ' --'

            for proc in processes:
                #Execute round for each process
                proc.do_round()

            #Deliver msgs for next round
            self.deliver_msgs(processes, 'UNICAST')

            #Check if needs to continue executing
            working = False
            for proc in processes:
                working = True if proc.sent_msg or proc.rcvd_msg else working
                
            if working:
                #Increase latencies
                for sender in senders:
                    sender[1] = sender[1] + 1

        latency = -1
        for sender in senders:
            latency = sender[1] if latency < sender[1] else latency

        self.print_results(self.nproc, turn-1, latency, (len(senders), turn-1))


    def sim_bcpipe(self):
        """Broadcasts a msg using unicast with pipe algorithm."""
        processes = []
        for i in range(0, self.nproc):
            processes.append(PipeProcess(i, processes))

        #Sender of the packet
        senders = [[random.randrange(self.nproc), 0]]
        processes[senders[0][0]].send_new = True
        
        #Execute rounds
        turn = 0
        working = True
        while working:
            turn = turn +1
            print '-- Round ' + str(turn) + ' --'

            for proc in processes:
                #Execute round for each process
                proc.do_round()

            #Deliver msgs for next round
            self.deliver_msgs(processes, 'UNICAST')

            #Check if needs to continue executing
            working = False
            for proc in processes:
                working = True if proc.sent_msg or proc.rcvd_msg else working
                
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
