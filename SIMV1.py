import simpy
import numpy as np
import matplotlib.pyplot as plt
import sys
from threading import Thread
"""
assuming the env.now is  in microsecond. 


"""

mon_t = []
que_len = []
def monitor(env, res):
    while True: 
        mon_t.append(env.now)
        que_len.append(len(res.items))
        yield env.timeout(10)#wait 10micorsecond between sampling

#calling resource method 
def call_res(res, env, p, out_rate): 
    #request a resource 
  
    print('{} :packet arrived at {}'.format(p, env.now))
    yield res.get(out_rate)
    print("{} :packet is being processed {}".format(p, env.now))
    yield env.timeout(out_rate)
    #yield env.timeout(np.random.exponential(1.0/3.0))
    print("{} :packet is departed {}".format(p ,env.now))
   
    
    

    
def calc_rate(mbps, pkt_size):
    byte = 8
    micro_sec = 10**6 # ten to the power of 6 = 1 micro second
    rate = (pkt_size *byte)/(mbps*micro_sec)
    return rate

    
def cross_traffic_gen(env, res, out_rate):
    pkt_Size = int(input('Eneter the packet size in bytes: '))
    #interval = float(input('Enter the interval rate between two packets in seconds: '))
    link_speed = int(input('Enter the input link rate in Mbps: '))

    inpt_rate = calc_rate(link_speed, pkt_Size)
    out_rate = calc_rate(out_rate,pkt_Size)


    if not pkt_Size and not link_speed: 
        print("All values needs to be entered.  Values given are Pakcet size given: {} packet size, {} link speed ) ".format(pkt_Size,link_speed))
    else: 
        print('================================================================================')
        print('input link rate is: {} (micro sec) '.format(inpt_rate))
        print('output link rate is: {} (micro sec)'.format(out_rate))
        print('================================================================================')
    print('\nPausing...  (Hit ENTER to continue, type quit to exit.)')
    
    try:
        response = input()
        if response == 'quit':
            sys.exit()
        else:
            print ('Resuming...')
    except KeyboardInterrupt:
        print ('Resuming...')
    
    flow1 = float(input('flow 1 rate in mbps: '))
    flow1_rate = calc_rate(flow1,pkt_Size)
    flow2 = float(input('flow 2 rate in mbps: '))
    flow2_rate = calc_rate(flow2,pkt_Size)
    """
    flow3 = float(input('flow 3 rate in mbps: '))
    flow3_rate = calc_rate(flow3,pkt_Size)

    print(flow1_rate, flow2_rate, flow3_rate)
    t_flow = flow1 + flow2 + flow3 
    if t_flow > link_speed:
        print('Total flow can not be more than {}mbps input link'.format(link_speed))
        sys.exit()
    """
    i = 0 
    while True:
        #create a packet 
        res.put(flow1_rate)
        env.process(call_res(res,env,i,out_rate))
        yield env.timeout(1)
        i+=1

        res.put(flow2_rate)
        env.process(call_res(res,env,i,out_rate))
        i+=1
        yield env.timeout(0.5)
        """
        env.process(call_res(res,env,i,out_rate))
        yield env.timeout(flow2_rate)#time in second.
        i+=1
        """
        

np.random.seed(0)
out_rate = int(input('Enter the output link rate in Mbps: '))
time = int(input('Enter time in Micro seconds, how long you want to run the simulation for: ')) 
env = simpy.Environment()
res = simpy.Store(env)
env.process(cross_traffic_gen(env, res, out_rate))
env.process(monitor(env, res))
env.run(until=time) 
#drat the plot
plt.figure()
plt.step(mon_t, que_len, where='post')
plt.xlabel('time (\u00B5)')
plt.ylabel('Queue length(packets)')
plt.show()
