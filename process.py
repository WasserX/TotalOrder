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
        self.quant_delivered = 0 #Counts delivered msgs. Used to know when to finish simulation. Not used in algorithms.
        self.clock = 0 + pid / n_proc

    def send_msg(self):
        """Sends a msg that is in the sending queue"""
        if self.to_send:
            msg, to = self.to_send.pop(0)
            packet = (self.pid, to, msg)
            
            self.send_queue.append(packet)
            #print 'PID ' + str(self.pid) + ' sent msg ' + str(msg) + ' to ' + str(to.pid)
            
            self.clock = self.clock + 1
        return

    def create_dest_list(self, msg):
        """This method will change according to policy. Establishes the order
        that will be used to broadcast the msg"""
        self.quant_delivered += 1
        for proc in self.others:
            if proc != self:
                self.to_send.append((msg, proc))

    def on_msg(self):
        msg = self.to_receive.pop(0)
        rcvd_clock, rcvd_pid, content = msg
        self.quant_delivered += 1
        self.clock = max(self.clock, rcvd_clock) +1
        
        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)
 

    def do_round(self):
        """Process a simple round"""
        if self.send_new:
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
        clock, pid, content = msg

        try:
            index = self.sending_order.index(msg[0])
            self.to_send = self.sending_order[index+1]
            return
        except ValueError: #If it does not exists, create a list and make it global
            self.quant_delivered += 1
            self.to_send = []
            for proc in self.others:
                if proc != self:
                    self.to_send.append((msg, proc))
            
            self.sending_order.append(self.clock)
            self.sending_order.append(self.to_send)
             
    def on_msg(self):
        msg = self.to_receive.pop(0)
        self.create_dest_list(msg)
        self.quant_delivered += 1
        
        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)


class PipeProcess(Process):
    def create_dest_list(self, msg):
        """In pipeline, only send msg to next process. Circular list. If dest is the sender, stop."""
        clock, pid, content = msg
        if pid == self.pid:
            self.quant_delivered += 1
        normalized_dest = (self.pid + 1) % self.nproc
        if normalized_dest != msg[0]:
            self.to_send.append((msg, self.others[normalized_dest]))

    def on_msg(self):
        """When a msg is received. Send it to the next process."""
        msg = self.to_receive.pop(0)
        clock, pid, content = msg
        self.quant_delivered += 1
    
        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)

        if pid != self.pid:
            self.create_dest_list(msg)
            
            
class TOProcess(Process):
    def __init__(self, pid, n_proc, others, send_queue):
        Process.__init__(self, pid, n_proc, others, send_queue)
        self.to_ack = [] #Messages received but that did not get all the acks yet. Format: [(msg, [acks_rcvd])]
        
    def on_msg(self):
        msg = self.to_receive.pop(0)
        rcvd_clock, rcvd_pid, content = msg
        
        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)
        
        self.clock = max(self.clock, rcvd_clock) +1
        
        if content != 'ACK':
            ack_packet = (rcvd_clock, self.pid, 'ACK')
            self.create_dest_list(ack_packet)
            self.ack_msg(ack_packet)
        
        self.ack_msg(msg)
        
    def create_dest_list(self, msg):
        clock, pid, content = msg
        
        if content != 'ACK':
            self.ack_msg(msg)
            
        new_to_send = []
        for proc in self.others:
            if proc != self:
                new_to_send.append((msg, proc))
        
        for i, packet in enumerate(self.to_send):
            pack_msg, proc = packet
            if pack_msg[0] > clock:
                self.to_send[i:i] = new_to_send
                return
        
        self.to_send.extend(new_to_send)
                
    
    def deliver(self, msg):
        print 'Message ' + str(msg) + ' Delivered in ' + str(self.pid)
        self.quant_delivered += 1

    
    def ack_msg(self, msg):
        """Received an acknowledge of msg sent by process pid. Add it to list of ackd msgs.
        If msg has been acknowledged by everyone, deliver it."""
        #If the list exists, add ack to list, otherwise create the list.
        clock, pid, content = msg
        ackd_msg_exists = False

        for i, element in enumerate(self.to_ack):
            ack_clock, ack_pid, ack_content = element[0]
            ack_proc_list = element[1]

            if ack_clock == clock:
                if content != 'ACK':
                    self.to_ack.pop(i)
                    self.to_ack.insert(i, ((clock, pid, content), ack_proc_list))
                ack_proc_list.append(pid)
                ackd_msg_exists = True
                
        if not ackd_msg_exists:   
            self.to_ack.append((msg, [pid]))
            self.to_ack.sort()

        #Test if acknowledged by everyone, in that case deliver it
        msg, acks = self.to_ack[0]
        if len(acks) == self.nproc:
            self.to_ack.pop(0)
            self.deliver(msg)
        