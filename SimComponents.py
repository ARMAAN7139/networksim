"""
    A bit more detailed set of components to use in packet switching
    queueing experiments.
    Copyright 2014 Greg M. Bernstein
    Released under the MIT license
"""
import simpy
import random
import copy
from simpy.core import BoundClass
from simpy.resources import base
from heapq import heappush, heappop


class Packet(object):
    """ A very simple class that represents a packet.
        This packet will run through a queue at a switch output port.
        We use a float to represent the size of the packet in bytes so that
        we can compare to ideal M/M/1 queues.

        Parameters
        ----------
        time : float
            the time the packet arrives at the output queue.
        size : float
            the size of the packet in bytes
        id : int
            an identifier for the packet
        src, dst : int
            identifiers for source and destination
        flow_id : int
            small integer that can be used to identify a flow
    """
    def __init__(self, time, size, id, src="a", dst="z", flow_id=0):
        self.time = time
        self.size = size
        self.id = id
        self.src = src
        self.dst = dst
        self.flow_id = flow_id
    def __repr__(self):
        return "id: {}, src: {}, time: {}, size: {}".\
            format(self.id, self.src, self.time, self.size)


class PacketGenerator(object):
    """ Generates packets with given inter-arrival time distribution.
        Set the "out" member variable to the entity to receive the packet.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        adist : function
            a no parameter function that returns the successive inter-arrival times of the packetsf the packets
        sdist : function
            a no parameter function that returns the successive sizes of the packets
        initial_delay : number
            Starts generation after an initial delay. Default = 0
        finish : number
            Stops generation at the finish time. Default is infinite


    """
    def __init__(self, env, id,  adist, sdist, initial_delay=0, finish=float("inf"), flow_id=0):
        self.id = id
        self.env = env
        self.adist = adist
        self.sdist = sdist
        self.initial_delay = initial_delay
        self.finish = finish
        self.out = None
        self.packets_sent = 0
        self.action = env.process(self.run())  # starts the run() method as a SimPy process
        self.flow_id = flow_id


    def run(self):
        """The generator function used in simulations.
        """
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            # wait for next transmission
            yield self.env.timeout(self.adist)
            self.packets_sent += 1
            p = Packet(self.env.now, self.sdist, self.packets_sent, src=self.id, flow_id=self.flow_id)
            self.out.put(p)
          


class PacketSink(object):
    """ Receives packets and collects delay information into the
        waits list. You can then use this list to look at delay statistics.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        debug : boolean
            if true then the contents of each packet will be printed as it is received.
        rec_arrivals : boolean
            if true then arrivals will be recorded
        absolute_arrivals : boolean
            if true absolute arrival times will be recorded, otherwise the time between consecutive arrivals
            is recorded.
        rec_waits : boolean
            if true waiting time experienced by each packet is recorded
        selector: a function that takes a packet and returns a boolean
            used for selective statistics. Default none.
        res: environment resourse to process the packets.

    """
    def __init__(self, env, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None):
        self.store = simpy.Store(env)
        self.env = env
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits = []
        self.arrivals = []
        self.debug = debug
        self.packets_rec = 0
        self.bytes_rec = 0
        self.selector = selector
        self.last_arrival = 0.0
        self.res = simpy.Resource(env,capacity=1)
        
    def calc_rate(self,mbps, packet_Size):
        "method to calculate link rates"
        byte = 8
        micro_sec = 10**6 # ten to the power of 6 = 1 micro second
        rate = (packet_Size *byte)/(mbps * micro_sec)
        return rate


    def call_res(self,pkt):
        #request a resource 
        with self.res.request() as req:
            try:
                print('{} :packet arrived at {:f}'.format(pkt.src, self.env.now))
                yield req
                print("{} :packet is being  processed {:f}".format(pkt.src, self.env.now))
                yield self.env.timeout(self.calc_rate(100,pkt.size))
                print("{} :packet is departed {:f}".format(pkt.src , self.env.now))
            except simpy.Interrupt:
                print("Inturrepted by simpy {:f}".format(self.env.now)) 

    def put(self, pkt):
        if not self.selector or self.selector(pkt):
            now = self.env.now
            self.env.process(self.call_res(pkt))
            if self.rec_waits:
                self.waits.append(self.env.now - pkt.time)
            if self.rec_arrivals:
                if self.absolute_arrivals:
                    self.arrivals.append(now)
                else:
                    self.arrivals.append(now - self.last_arrival)
                self.last_arrival = now
            self.packets_rec += 1
            self.bytes_rec += pkt.size
            if self.debug:
               print(pkt)

