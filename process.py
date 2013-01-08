class Process:
    def __init__(self, pid, others):
        self.pid = pid
        self.others = others
        self.send_new = False #Flag to tell if needs to send a new msg in the current round
        self.sent_msg = None #Message that will be delivered next round
        self.rcvd_msg = None #Message that was sent to us last round
        self.to_send = [] #Remaining processes that need to receive a msg
        self.msgcount = 0

    def send_msg(self):
        """Sends a msg that is in the sending queue"""
        if self.sent_msg:
            return #If we have already sent a msg. Just return.
        for elem in self.to_send:
            if elem[1]:
                dest = elem[1].pop()
                self.sent_msg = (dest, elem[0])
                print 'PID ' + str(self.pid) + ' sent msg ' + str(elem[0]) + ' to ' + str(dest.pid)
                return

    def create_dest_list(self, msg):
        """This method will change according to policy. Establishes the order
        that will be used to broadcast the msg"""
        self.to_send = [[msg, [] + self.others]]
        del self.to_send[0][1][self.pid]

    def on_rcvd_msg(self):
        #print 'PID ' + str(self.pid) + ' received msg ' + str(self.rcvd_msg)
        self.rcvd_msg = None

    def do_round(self):
        """Process a simple round"""
        if self.send_new:
            self.create_dest_list((self.pid, self.msgcount, 'DATA'))
            self.msgcount = self.msgcount + 1
            self.send_new = False
        
        if self.rcvd_msg:
            self.on_rcvd_msg()

        self.send_msg() #If we have something to send, send it
        

class TreeProcess(Process):
    def __init__(self, pid, others, delivery_order):
        Process.__init__(self, pid, others)
        self.delivery_order = delivery_order

    def create_dest_list(self, msg):
        for global_queue in self.delivery_order:
            if global_queue[0] == msg[0] and global_queue[1] == msg[1]:
                self.to_send.append([msg, global_queue[2]])
                return
        
        dest_list = (msg[0], msg[1], [] + self.others)
        del dest_list[2][self.pid]
        
        self.delivery_order.append(dest_list)
        self.to_send.append([msg, self.delivery_order[len(self.delivery_order)-1][2]])
        
    def on_rcvd_msg(self):
        self.create_dest_list(self.rcvd_msg)
        self.rcvd_msg = None
