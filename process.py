from __future__ import division

class Process:
    def __init__(self, pid, n_proc, others, send_queue):
        self.pid = pid
        self.others = others
        self.nproc = n_proc
        self.send_new = False #Flag to tell if needs to send a new msg in the current round
        
        #Message to send in a round must be added to this queue.(Only one accepted per round).
        #Format: (emitter, to, msg) emitter can be different than original sender
        self.send_queue = send_queue
        
        self.to_receive = [] #Queue of messages that need to be processed. One message will be processed per round
        self.to_send = [] #Remaining msgs that need to be sent. Format: [(msg, to)]
        self.clock = 0 + pid / n_proc

    def send_msg(self):
        """Sends a msg that is in the sending queue"""
        if self.to_send:
            msg, to = self.to_send.pop(0)
            packet = (self.pid, to, msg)
            
            self.send_queue.append(packet)
            print 'PID ' + str(self.pid) + ' sent msg ' + str(msg) + ' to ' + str(to.pid)
            
            self.clock = self.clock + 1
        return

    def create_dest_list(self, msg):
        """This method will change according to policy. Establishes the order
        that will be used to broadcast the msg"""
        for proc in self.others:
            if proc != self:
                self.to_send.append((msg, proc))

    def on_msg(self):
        rcvd_clock, rcvd_pid, content = self.to_receive.pop(0)
        self.clock = max(self.clock, rcvd_clock) +1

    def do_round(self):
        """Process a simple round"""
        if self.send_new and not self.to_send:
            self.create_dest_list((self.clock, self.pid, 'DATA'))
            self.send_new = False
            
        if self.to_receive:
            self.on_msg()

        self.send_msg() #If we have something to send in the queue, send it
        

class TreeProcess(Process):
    def __init__(self, pid, n_proc, others, send_queue, sending_order):
        Process.__init__(self, pid, n_proc, others, send_queue)
        self.sending_order = sending_order

    def create_dest_list(self, msg):
        #Check if remaining process list already exists
        try:
            index = self.sending_order.index(msg[1])
            self.to_send = self.sending_order[index+1]
            return
        except ValueError: #If it does not exists, create a list and make it global
            self.to_send = []
            for proc in self.others:
                if proc != self:
                    self.to_send.append((msg, proc))
            
            self.sending_order.append(self.clock)
            self.sending_order.append(self.to_send)
             
    def on_msg(self):
        self.create_dest_list(self.to_receive.pop(0))
        

class PipeProcess(Process):
    def create_dest_list(self, msg):
        """In pipeline, only send msg to next process. Circular list. If dest is the sender, stop."""
        normalized_dest = (self.pid + 1) % self.nproc
        if normalized_dest != msg[0]:
            self.to_send.append((msg, self.others[normalized_dest]))

    def on_msg(self):
        """When a msg is received. Send it to the next process."""
        clock, pid, content= self.to_receive.pop(0)
        
        if pid != self.pid:
            self.create_dest_list(msg)
            
            
class TOProcess(Process):
    def __init__(self, pid, n_proc, others, send_queue):
        Process.__init__(self, pid, n_proc, others, send_queue)
        self.to_ack = [] #Messages received but that did not get all the acks yet. Format: [(msg, [acks_rcvd])]
        
    def on_msg(self):
        msg = self.to_receive.pop(0)
        rcvd_clock, rcvd_pid, content = msg
        self.clock = max(self.clock, rcvd_clock) +1
        
        if content == 'DATA':
            self.create_dest_list((rcvd_clock, self.pid, 'ACK'))
            self.ack_msg(msg)
        else:
            self.ack_msg(msg)
        
    def create_dest_list(self, msg):
        clock, pid, content = msg
        if content == 'DATA':
            self.to_ack.append((msg, [pid]))
            
        for proc in self.others:
            if proc != self:
                self.to_send.append((msg, proc))
        
    
    def deliver(self, msg):
        print 'Message ' + str(msg) + ' Delivered in ' + str(self.pid) 
    
    def ack_msg(self, msg):
        """Received an acknowledge of msg sent by process pid. Add it to list of ackd msgs.
        If msg has been acknowledged by everyone, deliver it."""
        #If the list exists, add ack to list, otherwise create the list.
        #In the
        clock, pid, content = msg
        ackd_msg_exists = False
        

        for i, element in enumerate(self.to_ack):
            ack_clock, ack_pid, ack_content = element[0]
            ack_proc_list = element[1]
            if ack_clock == clock:
                if content == 'DATA':
                    print self.to_ack[i]
                    self.to_ack.pop(i)
                    self.to_ack.insert(i, ((ack_clock, ack_pid, 'DATA'), ack_proc_list))
                    print self.to_ack[i]
                ack_proc_list.append(pid)
                ackd_msg_exists = True
                
        if not ackd_msg_exists:   
            self.to_ack.append((msg, [pid]))
            self.to_ack.sort()
        else:
        #Test if acknowledged by everyone, in that case deliver it
            msg, acks = self.to_ack[0]
            if len(acks) == self.nproc:
                self.to_ack.pop(0)
                self.deliver(msg)
        