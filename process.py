#Messages are in the form (<sender id>, <destination|None>, <ACK|DATA>)


class Process:
    def __init__(self, pid, pids):
        self.pid = pid
        #All msgs that want to be sent are here. Simulator will send one per round FIFO.
        self.outbox = [] 
        self.received = None #Simulator will only pass one msg per round
        self.delivered = []
        self.to_deliver = []
        self.pids = pids
    
    def broadcast(self, mode='Multicast', dest=None):
        #Unicast
        if mode == 'Unicast':
            for i in range(0,self.pids):
                if i != self.pid:
                    self.outbox.append((self.pid, i, 'DATA'))
        #Multicast
        else: 
            self.outbox.append((self.pid, None, 'DATA'))
            
    def receive(self):
        a = 4
        #print self.received    
    
                
test = Process(3, 6)
test.broadcast("Multicast")
test.receive()
