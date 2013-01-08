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
        pass

    def do_round(self):
        """Process a simple round"""
        if self.send_new:
            self.create_dest_list((self.pid, self.msgcount, 'DATA'))
            self.msgcount = self.msgcount + 1
            self.send_new = False
        
        if self.rcvd_msg:
            #print 'PID ' + str(self.pid) + ' received msg ' + str(self.rcvd_msg)
            self.on_rcvd_msg()
            self.rcvd_msg = None
        
        self.send_msg() #If we have something to send, send it
