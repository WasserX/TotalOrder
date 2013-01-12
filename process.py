from __future__ import division
from math import log
from operator import itemgetter

class Process:

    def __init__(self, pid, n_proc, others, send_queue):
        self.pid = pid
        self.others = others
        self.nproc = n_proc
        self.send_new = False #Flag to tell if needs to send a new msg in the current round

        #Message to send in a round must be added to this queue.(Only one accepted per round).
        #Format: (emitter, to, msg) emitter can be different than original sender. Multicast is implied if to = None
        #Message Format: (clock, creator_pid, content)
        self.send_queue = send_queue

        self.to_receive = [] #Queue of messages that need to be processed. One message will be processed per round. Format: [msg]
        self.to_send = [] #Remaining msgs that need to be sent. Format: [(msg, to)]
        self.delivered = [] #Keeps track of delivered msgs. Used to know when to finish simulation. Not used in algorithms. Format: [clock,...]
        self.clock = 0 + pid / n_proc

    def send_msg(self):
        """Sends a msg that is in the sending queue"""

        if self.to_send:
            msg, to = self.to_send.pop(0)
            packet = (self.pid, to, msg)

            self.send_queue.append(packet)

            #To whom it sent the message
            dest = to.pid if to else 'everyone'
            print 'PID ' + str(self.pid) + ' sent msg ' + str(msg) + ' to ' + str(dest)

            self.clock += 1
        return

    def create_dest_list(self, msg):
        """This method will change according to policy. Establishes the order
        that will be used to broadcast the msg"""
        self.delivered.append(msg[0])
        for proc in self.others:
            if proc != self:
                self.to_send.append((msg, proc))

    def on_msg(self):
        msg = self.to_receive.pop(0)
        rcvd_clock, rcvd_pid, content = msg
        self.delivered.append(rcvd_clock)
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
    def __init__(self, pid, n_proc, others, send_queue):
        Process.__init__(self, pid, n_proc, others, send_queue)

    def create_dest_list(self, msg):
        clock, pid, content = msg
        if pid == self.pid:
            self.delivered.append(clock)

        for proc in self.get_remaining_proc_from_msg(msg):
            self.to_send.append((msg, proc))

    def get_remaining_proc_from_msg(self, msg):
        """Creates a list of processes that need to receive msg from us. Used when procs cooperate to send same msg."""
        """In other words. Here is the tree algorithm."""

        clock, pid, content = msg

        if pid == self.pid:
            exp = 0
        else:
            # not_modularized_pid is the value before doing mod nproc
            not_modularized_pid = self.pid if self.pid >= pid else self.pid + self.nproc

            not_modularized_pid -= pid
            # discover the exp of the received message and increments it to use it
            # this is the inverse function of pow(2,exp) + pid
            exp = int(log(not_modularized_pid, 2) + 1)

        next_remaining = (pow(2, exp) + self.pid)

        #If pid smaller than sender, send until the sender. Otherwise Reach the sender in a circular fashion
        stop_condition = pid if self.pid < pid else self.nproc + pid
        remaining = []
        while next_remaining < stop_condition:
            next_remaining = next_remaining  % self.nproc
            #does not add itself to list
            if next_remaining != self.pid:
                remaining.append(self.others[next_remaining])

            exp += 1
            next_remaining = (pow(2, exp) + self.pid)

        return remaining

    def on_msg(self):
        msg = self.to_receive.pop(0)
        clock, pid, content = msg
        self.create_dest_list(msg)
        self.delivered.append(clock)

        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)


class PipeProcess(Process):
    def create_dest_list(self, msg):
        """In pipeline, only send msg to next process. Circular list. If dest is the sender, stop."""
        clock, pid, content = msg
        if pid == self.pid:
            self.delivered.append(clock)
        normalized_dest = (self.pid + 1) % self.nproc
        if normalized_dest != pid:
            self.to_send.append((msg, self.others[normalized_dest]))

    def on_msg(self):
        """When a msg is received. Send it to the next process."""
        msg = self.to_receive.pop(0)
        clock, pid, content = msg
        self.delivered.append(clock)

        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)

        if pid != self.pid:
            self.create_dest_list(msg)


class TOLATProcess(TreeProcess):
    def __init__(self, pid, n_proc, others, send_queue):
        Process.__init__(self, pid, n_proc, others, send_queue)
        self.to_ack = {} #Messages received but that did not get all the acks yet. Format: {msg: <acks_rcvd>}
        self.delayed_sends = [] #Format: [[(msg,dest)],[(msg,dest)]]

    def on_msg(self):
        self.to_receive.sort(key=itemgetter(2, 0))
        msg = self.to_receive.pop(0)
        rcvd_clock, rcvd_pid, content = msg

        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)

        self.clock = max(self.clock, rcvd_clock) + 1

        #If we received a DATA msg. Send acks to everyone to tell them we received the msg.
        if content != 'ACK':
            self.create_dest_list(msg)

        self.ack_msg(msg)

    def create_dest_list(self, msg):
        clock, pid, content = msg
        temp_destinations = []

        #If we are sending the DATA msg to everyone, ACK the message to ourselves without using a round.
        if self.pid == pid:
            self.ack_msg(msg)
        
        #Help distribute data msgs even if we are not the senders
        destinations = self.get_remaining_proc_from_msg(msg)
        for proc in destinations:
            temp_destinations.append((msg, proc))
        
    
        #Add ACK msg to sending queue. Sending msg using Multicast. Only if we are not the sender
        if self.pid != pid:
            ack_packet = (clock, self.pid, 'ACK')
            temp_destinations.append((ack_packet, None))

        temp_destinations.sort(key=lambda x: x[0][0])
        temp_destinations.sort(key=lambda x: x[0][2], reverse=True)
    
        
        #Block sending queue until message is delivered
        if self.to_send and self.to_send[0][0][0] < clock:
            self.delayed_sends.append(temp_destinations)
        elif self.to_send:
            self.delayed_sends.append(self.to_send[:])
            self.to_send = temp_destinations
        else:
            self.to_send = temp_destinations


    def deliver(self, msg):
        print 'Message ' + str(msg) + ' Delivered in ' + str(self.pid)
        self.delivered.append(msg[0])
        
        #Unpause sending queue
        if self.delayed_sends:
            self.delayed_sends.sort(key=lambda x: x[0][0][0])
            self.to_send = self.delayed_sends.pop(0)

    def ack_msg(self, msg):
        """Received an acknowledge of msg sent by process pid. Add it to list of ackd msgs.
        If msg has been acknowledged by everyone, deliver it."""
        #If the list exists, add ack to list, otherwise create the list.
        clock, pid, content = msg

        try:
            self.to_ack[clock]['acks'] += 1
            if content != 'ACK':
                self.to_ack[clock]['msg'] = msg
        except KeyError:
            self.to_ack[clock] = {'msg': msg, 'acks': 1}

        #Test if acknowledged by everyone, in that case deliver it
        for clock in sorted(self.to_ack.iterkeys()):
            if self.to_ack[clock]['acks'] == self.nproc:
                self.deliver(self.to_ack[clock]['msg'])
                del self.to_ack[clock]
            else:
                return


class TOTHROUGHProcess(TreeProcess):
    def __init__(self, pid, n_proc, others, send_queue):
        Process.__init__(self, pid, n_proc, others, send_queue)
        self.to_ack = {} #Messages received but that did not get all the acks yet. Format: {msg: <acks_rcvd>}

    def on_msg(self):
        self.to_receive.sort(key=itemgetter(2, 0))
        msg = self.to_receive.pop(0)
        rcvd_clock, rcvd_pid, content = msg

        print 'Process ' + str(self.pid) + ' received msg: ' + str(msg)

        self.clock = max(self.clock, rcvd_clock) + 1

        #If we received a DATA msg. Send acks to everyone to tell them we received the msg.
        if content != 'ACK':
            self.create_dest_list(msg)

        self.ack_msg(msg)

    def create_dest_list(self, msg):
        clock, pid, content = msg

        #If we are sending the DATA msg to everyone, ACK the message to ourselves without using a round.
        if self.pid == pid:
            self.ack_msg(msg)
        
        #Help distribute data msgs even if we are not the senders
        destinations = self.get_remaining_proc_from_msg(msg)
        for proc in destinations:
            self.to_send.append((msg, proc))
        
    
        #Add ACK msg to sending queue. Sending msg using Multicast. Only if we are not the sender        
        if self.pid != pid:
            ack_packet = (clock, self.pid, 'ACK')
            self.to_send.append((ack_packet, None))
            
        self.to_send.sort(key=lambda x: x[0][0])
        self.to_send.sort(key=lambda x: x[0][2], reverse=True)


    def deliver(self, msg):
        print 'Message ' + str(msg) + ' Delivered in ' + str(self.pid)
        self.delivered.append(msg[0])

    def ack_msg(self, msg):
        """Received an acknowledge of msg sent by process pid. Add it to list of ackd msgs.
        If msg has been acknowledged by everyone, deliver it."""
        #If the list exists, add ack to list, otherwise create the list.
        clock, pid, content = msg

        try:
            self.to_ack[clock]['acks'] += 1
            if content != 'ACK':
                self.to_ack[clock]['msg'] = msg
        except KeyError:
            self.to_ack[clock] = {'msg': msg, 'acks': 1}

        #Test if acknowledged by everyone, in that case deliver it
        for clock in sorted(self.to_ack.iterkeys()):
            if self.to_ack[clock]['acks'] == self.nproc:
                self.deliver(self.to_ack[clock]['msg'])
                del self.to_ack[clock]
            else:
                return                