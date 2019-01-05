import simpy
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time as tm
import pprint
from SimComponents import PacketGenerator, PacketSink



#assuming the env.now is  in microsecond. 
"""global variables"""

mon_t = []  # list for keeping track of time for graphs. 
que_len = []   # list for que_len in packet size
Compression = []  # list for difference betweet MG and EG
Decompression = []
No_change = []


def monitor(env, res):
    """"method to calculate the length of the resource
        IT take reousece an environment parameters """
    while True: 
        mon_t.append(env.now)
        que_len.append(len(res.queue))
        yield env.timeout(0.000005)#wait 10micorsecond between sampling

def expected_Gap(): 
    """method to calculate expected gap"""
    st = 1000  #size of the trailing packet. 
    li = 100 #link rate respectivley
    sh = 64  #size of the heading packet
    power6 = 10 ** 6
    dispercion_Gap = abs(((st*8)/(li*power6)) - ((sh*8)/(li*power6)))  # dispercsiom gap calculation
    EG = abs((st*8/li*power6) + dispercion_Gap)  #expected gap calculation. take absolute value of it
    return EG

def measured_Gap(EG, tqh, tqt): 
    "mthod ot calculate measured gap."
    MG = abs(EG - (tqt - tqh))
    return MG

def compare_result(EG, MG):
    "#method to compare the result"
    if EG > MG:
        Compression.append(MG - EG)
    elif EG < MG:
        Decompression.append(MG - EG)
    elif EG == MG: 
        No_change.append(str(MG) + "   "+   str(EG))
    else: 
       print("THIS IS NOT WORKING")

def calc_rate(mbps, PacketGenerator_size):
    "method to calculate link rates"
    byte = 8
    micro_sec = 10**6 # ten to the power of 6 = 1 micro second
    rate = (PacketGenerator_size *byte)/(mbps * micro_sec)
    return rate


def log(arrivals, depature,Compression): 
    "Method to log both values recorded from the ph and pt Despercision gaps"
    with open("C:\\Users\\Joykill\\Desktop\\sim_project\\logs.txt", "a+") as wr:
        wr.write("**********************______Arrivals_____***************************************************" + "\n")
        wr.write("\t\t\t" + str(arrivals) + "\n")
        wr.write("**********************______Departure____*****************************************" + "\n")
        wr.write("\t\t\t" + str(depature) + "\n")
        wr.write("*********************_______Compression________***************************************"+ "\n")
        wr.write(str(Compression)+ "\n")
        wr.write("----------------------------------time is:  " + tm.strftime("%Y%m%d-%H%M%S")+'---------------------------\n')


def cross_traffic_gen(env):
    #out_rate = int(input('Enter the output link rate in Mbps: '))
   
    out_rate = 100
    #PacketGenerator_Size = int(input('Eneter the packet size in bytes: '))
    #PacketGenerator_Size = np.random.uniform(10, 1000)
    PacketGenerator_Size = 1000
    #link_speed = int(input('Enter the input link rate in Mbps: '))
    link_speed = 100
    inpt_rate = calc_rate(link_speed, PacketGenerator_Size)
    outpt_rate = calc_rate(out_rate, PacketGenerator_Size)
    

    if not PacketGenerator_Size and not link_speed: 
        print("All values needs to be entered.  Values given are Pakcet size given: {} packet size, {} link speed ) ".format(PacketGenerator_Size,link_speed))
    else: 
        print('================================================================================')
        print('input link rate is: {:f} (micro sec) '.format(inpt_rate))
        print('output link rate is: {:f} (micro sec)'.format(outpt_rate))
        print('================================================================================')
    print('\nPausing...  (Hit ENTER to continue, type quit or q  to exit.)')
    
    """
    try:
        response = input()
        if response == 'quit' or response == 'q':
            sys.exit()
        else:
            print ('Resuming...')
    except KeyboardInterrupt:
        print ('Resuming...')
    """
    #flow1 = float(input('flow 1 rate in mbps: '))
    #flow1 = np.random.uniform(0, 10.0)
    flow1 = 30.00355254873293
    flow1_rate = calc_rate(flow1,PacketGenerator_Size)
    #flow2 = float(input('flow 2 rate in mbps: '))
    #flow2 = np.random.uniform(0, 30.0)
    flow2 = 19.244066606701242
    flow2_rate = calc_rate(flow2,PacketGenerator_Size)
    #flow3 = float(input('flow 3 rate in mbps: '))
    #flow3 = np.random.uniform(10.1, 25.5 )
    flow3 = 15.885632976835758
    flow3_rate = calc_rate(flow3,PacketGenerator_Size)
    #flow4 = float(input('flow 4 rate in mbps: '))
    #flow4 = np.random.uniform(20, 30.5)
    flow4 = 1.8086632189748015
    flow4_rate = calc_rate(flow4,PacketGenerator_Size)

    print("Flow rates are: " + str(flow1_rate) +";\t "+ str(flow2_rate) + ";\t "+str(flow3_rate)+"; \t"+ str(flow4_rate))
    t_flow = flow1 + flow2 + flow3 + flow4
    if t_flow > out_rate:# the total flow can not exceed  output link 
        print('Total flow can not be more than {}mbps input link'.format(out_rate))
        sys.exit(1)


    with open("C:\\Users\\Joykill\\Desktop\\sim_project\\compression.txt", "a+") as f: 
        t = (str(flow1_rate) + '|' + str(flow2_rate)+' |' + str(flow3_rate) + '|' + str(flow4_rate))
        f.write("\t\t\t" + str(flow1) + '\n')
        f.write("\t\t\t" +str(flow2)+ '\n')
        f.write("\t\t\t" +str(flow3)+ '\n')
        f.write("\t\t\t" +str(flow4)+ '\n')
        f.write(t+ '\n')
        f.write("time is:  " + tm.strftime("%Y%m%d-%H%M%S")+'---------------------------\n')
  
    return inpt_rate, outpt_rate, flow1_rate, flow2_rate, flow3_rate, PacketGenerator_Size, flow4_rate

def main(): 
    """main method"""
    #tmp var time = int(input('Enter time in Micro seconds, how long you want to run the simulation for: ')) 
    env = simpy.Environment()
    pram = cross_traffic_gen(env )# store it in param tuple. 
    print(pram)
    # packet generator takes environmetn, label, link rate, packet size, initial delay( defaulted to 0 )
    p0  = PacketGenerator(env,'flow1',pram[2],pram[5])
    p1  = PacketGenerator(env,'flow2',pram[3],pram[5])
    p2  = PacketGenerator(env,'flow3',pram[4],pram[5])
    p3  = PacketGenerator(env,'flow4',pram[6],pram[5])

    #Probing packets with no Intraprobe gap. 
    #ph  = PacketGenerator(env,'ph',0.0001, 64)
    #pt = PacketGenerator(env, 'pt',0.0002, 1000)

    # packet sink to monitor the packets.
    ps  = PacketSink(env,debug=True)
    
    p0.out = ps 
    p1.out = ps 
    p2.out = ps
    p3.out = ps
    #ph.out = ps
    #pt.out = ps

    env.process(monitor(env,ps.res))
    env.run(10)
    print(ps.packets_rec)
   
   
    #draw the plot
    plt.figure()
    plt.plot(mon_t,que_len)
    plt.xlabel('time (\u00B5)')
    plt.ylabel('Queue length(packets)')
    picName = "plot" + tm.strftime("%Y%m%d-%H%M%S") + '.png'
    plt.savefig(os.sep.join([os.path.expanduser('~'), 'Desktop\\compression_graphs', picName ]))
    plt.show()

if __name__ == "__main__": 
    main()

