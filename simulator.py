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
            for i in range(0, self.nproc):
                self.processes.append(TreeProcess(i, self.nproc, self.processes, self.send_queue))
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

    def send_msgs(self):
        """Simulates the msg transfer. Essentially puts the msg of the sender in the destination."""
        """If the msg was marked as multicast, will replicate it for all processes."""
        
        for sender, to, msg in self.send_queue:
            to.to_receive.append(msg)

        del self.send_queue[:]


    def sim_broadcast(self):
        """Broadcasts a msg without acks using the processes algorithm to spread"""

        #Order list of new msgs
        self.new_msgs_schedule.sort()

        #Execute rounds
        turn = 0
        latency = -1
        msg_latencies = {}
        delivered_msgs = {}
        deliveries_to_stop = self.nproc*len(self.new_msgs_schedule)
        working = True
        while working:
            turn += 1
            print '-- Round ' + str(turn) + ' --'

            #See if a new msg needs to be created in this round and set flags accordingly
            for msg_turn, pid in self.new_msgs_schedule:
                if msg_turn == turn:
                    self.processes[pid].send_new = True #Set flag to tell sender to create new msg
                    msg_latencies[self.processes[pid].clock] = 0

            for proc in self.processes:
                #Execute round for each process
                proc.do_round()

            #Send msgs for next round
            self.send_msgs()
            
            
            #Count delivered messages in the round and add them to the values that we had from old rounds
            for proc in self.processes:
                for clock in proc.delivered:
                    try:
                        delivered_msgs[clock]['counter'] += 1
                    except KeyError:
                        delivered_msgs[clock] = {'counter': 1, 'delivered': False}
                    proc.delivered.remove(clock)        
            #When a delivery is done to all messages, mark it as finished and stop counting its latency
            for clock, v in delivered_msgs.iteritems():
                if v['counter'] == self.nproc and not v['delivered']:
                    latency = max(latency, msg_latencies[clock])
                    del msg_latencies[clock]
                    v['delivered'] = True
                    deliveries_to_stop -= v['counter']

            #Stop working when nb of delivered msgs is equal to all delivered msgs.
            working = True if deliveries_to_stop else False

            if working:
                #Increase latencies
                for k in msg_latencies:
                    msg_latencies[k] += 1
        self.print_results(self.nproc, turn-1, latency, (len(self.new_msgs_schedule), turn-1))


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