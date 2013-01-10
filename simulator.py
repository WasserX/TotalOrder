from process import *
import argparse

class Simulator:
    def __init__(self):
        self.nproc = 0

    def simulate(self, mode, nproc, new_msgs_schedule):
        """Simulates a broadcast or a Total Order Broadcast. Available modes are
        'BCUNI', 'BCTREE', 'BCPIPE', 'TOLAT', 'TOTHROUGH'. 
        nproc defines the number of processes in the simulation"""
        
        self.nproc = nproc #Number of processes to simulate
        self.new_msgs_schedule = new_msgs_schedule #When should a process send a new message. If Already sending, will enqueue. Format: [(turn, pid)]
        self.processes = [] #References to processes
        self.send_queue = [] #Internal list used to distribute messages
        
        if mode == 'BCUNI':
            for i in range(0, self.nproc):
               self.processes.append(Process(i, self.nproc, self.processes, self.send_queue))
            self.sim_broadcast()
        elif mode == 'BCTREE':
            sending_order = []
            for i in range(0, self.nproc):
                self.processes.append(TreeProcess(i, self.nproc, self.processes, self.send_queue, sending_order))
            self.sim_broadcast()
        elif mode == 'BCPIPE':
            for i in range(0, self.nproc):
                self.processes.append(PipeProcess(i, self.nproc, self.processes, self.send_queue))
            self.sim_broadcast()
        elif mode == 'TOLAT':
            for i in range(0, self.nproc):
                self.processes.append(TOProcess(i, self.nproc, self.processes, self.send_queue))
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
        
        
        #Order list of new msgs
        self.new_msgs_schedule.sort()

        #Execute rounds
        turn = 0
        working = True
        msg_latencies = []
        while working:
            turn = turn +1
            print '-- Round ' + str(turn) + ' --'

            #See if a new msg needs to be created in this round and set flags accordingly
            for msg_turn, pid in self.new_msgs_schedule:
                if msg_turn == turn:
                    self.processes[pid].send_new = True #Set flag to tell sender to create new msg
                    msg_latencies.append([self.processes[pid].clock, 0])

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
                for latency in msg_latencies:
                    latency[1] = latency[1] + 1

        biggest_latency = -1
        for latency in msg_latencies:
            biggest_latency = latency[1] if biggest_latency < latency[1] else biggest_latency

        self.print_results(self.nproc, turn-1, biggest_latency, (len(msg_latencies), turn-1))


    def print_results(self, nproc, rounds, latency, throughput):
        print '-- Simulation Ended --'
        print 'Results:'
        print '    Nb of Processes: ' + str(nproc)
        print '    Rounds: ' + str(rounds)
        print '    Latency: ' + str(latency)
        print '    Throughput: ' + str(throughput[0]) + '/' + str(throughput[1])




def main():
    parser = argparse.ArgumentParser(description='Simulate Broadcasts and Total Order Broadcast algorithms.')
    parser.add_argument('filename', metavar='filename', type=str,
                   help="""Settings file with parameters to simulate. See example in README""")

    args = parser.parse_args()
    settings = open(args.filename, 'r')
    mode = settings.readline().strip()
    nproc = int(settings.readline().strip())
    schedule = [line.strip() for line in settings.readlines()]
    new_msgs_schedule = []
    for new_msg_timing in schedule:
        turn, pid = new_msg_timing.split()
        new_msgs_schedule.append((int(turn), int(pid)))
    
    simulator = Simulator()
    simulator.simulate(mode, nproc, new_msgs_schedule)
    
main()