"""
Simple example of PacketGenerator and PacketSink from the SimComponents module.
Creates two constant rate packet generators and wires them to one sink.
Copyright 2014 Dr. Greg M. Bernstein
Released under the MIT license
"""
import random 
from random import expovariate
import simpy
from SimComponents import PacketGenerator, PacketSink
from threading import Thread


def constArrival():  # Constant arrival distribution for generator 1
    return 1.5

def constArrival2():
    return 2.0

def distSize(): #size of the packet
    return expovariate(0.01)

def delay():
    return random.randint(1,100)
if __name__ == '__main__':
    env = simpy.Environment()  # Create the SimPy environment
    # Create the packet generators and sink
    ps = PacketSink(env, debug=True)  # debugging enable for simple output
    pg = PacketGenerator(env, "PH", constArrival, distSize, )
    pg2 = PacketGenerator(env, "PT", constArrival2, distSize, )
    # Wire packet generators and sink together
    pg.out = ps
    pg2.out = ps

    env.run(2000) # Run it
