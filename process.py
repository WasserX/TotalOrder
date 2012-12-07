#Messages are in the form (<sender id>, <msgid>, <ACK|DATA>)


class Process:
    def __init__(self, pid, pids):
        self.pid = pid
        #All msgs that want to be sent are here. Simulator will send one per round FIFO.
        self.outbox = [] 
        self.received = None #Simulator will only pass one msg per round
        self.delivered = []
        self.to_deliver = []
        self.pids = pids
        self.msgid = 0 #Counter for broadcasted msgids
    
    def broadcast(self, mode='Multicast', order=None):
        """Broadcast a msg. If Unicast mode, order of broadcast can be sent."""
        #Unicast
        if mode == 'Unicast':
            for i in order or range(0,self.pids):
                if i != self.pid:
                    self.outbox.append((i, (self.pid, self.msgid, 'DATA')))
        #Multicast
        else: 
            self.outbox.append((None, (self.pid, self.msgid, 'DATA')))
            
        self.msgid+= 1
            
    def receive(self):
        self.received = None
            
