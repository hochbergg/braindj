from scipy.fftpack import fft
import socket
import struct
import httplib
import time
import thread

SAMPLES_PER_WINDOW = 500
COLLECTION_FREQUENCY = 500
APP_IP = "172.20.10.9"

ONLINE = 1
OFFLINE = 2

SAMPLE_RANGE_IN_SEC = 10
REQUIRED_BYTES_LEN = 4*8

client = None

class MeiriFilter(object):
    def __init__(self,song_channels):
        self._channels = song_channels

    def do_filter(self,chan1,chan2,min_freq,max_freq,op=lambda a,b: a+b):
        chan1_data = self._channels[chan1]
        chan2_data = self._channels[chan2]

        data = [op(a,b) for a,b in zip(chan1_data,chan2_data)]
        windows = [data[i:i+SAMPLES_PER_WINDOW] for i in range(0,len(data),SAMPLES_PER_WINDOW)]
        fs = [fft(w) for w in windows]
        min_freq_bin = int(min_freq / (COLLECTION_FREQUENCY *1. / SAMPLES_PER_WINDOW))
        max_freq_bin = int(max_freq / (COLLECTION_FREQUENCY *1. / SAMPLES_PER_WINDOW))

        powers = [sum(abs(f[i])**2 for i in range(min_freq_bin,max_freq_bin+1)) for f in fs]

        return powers

BEST_SONG = 1
WORST_SONG = 5

def do_alpha_gamma_marker(frame):
    mf = MeiriFilter(frame)
    alpha = mf.do_filter(7,0,8,13)
    gamma = mf.do_filter(7,0,25,40)

    m = [a/b for a,b in zip(alpha,gamma)]
    return sum(m) / len(m)

def do_alpha_beta_marker(frame):
    mf = MeiriFilter(frame)
    alpha = mf.do_filter(7,0,8,13)
    beta = mf.do_filter(7,0,13,25)

    m = [a/b for a,b in zip(alpha,beta)]
    return sum(m) / len(m)

def do_alpha_beta_marker_2(frame):
    mf = MeiriFilter(frame)
    alpha = mf.do_filter(1,2,8,13)
    beta = mf.do_filter(1,2,13,25)

    m = [a/b for a,b in zip(alpha,beta)]
    return sum(m) / len(m)

# THIS IS THE FUNCITON YOU WANT TO CALL
# INPUT: frame = array of 8 channels, each channel is raw data (after unpack, before fft)
# OUTPUT: A number between 0 and 1 - 0 is BAD 1 is GOOD
def do_marker(frame):
    ms = [f(frame) for f in [do_alpha_gamma_marker,do_alpha_beta_marker,do_alpha_beta_marker_2]]
    raw = sum(ms)
    return raw

def init_online():
    global client
    client = socket.socket(socket.AF_INET)
    client.connect((APP_IP, 1234))
    
def init_offline():
    global client
    client = open("sample.bin", "rb")

def read_data_online():
    data = client.recv(REQUIRED_BYTES_LEN)
    if len(data)<REQUIRED_BYTES_LEN:
        data+=client.recv(REQUIRED_BYTES_LEN-len(data))
    return data

def read_data_offline():
    data = client.read(REQUIRED_BYTES_LEN)
    time.sleep(float(1)/500)
    return data

def analayse_nothing(channelMatrix):
    return 0

init_func = None
read_data_func = None

analyse_func = analayse_nothing
 
channelMatrix = [[],[],[],[],[],[],[],[]]
mode = ONLINE
sampleLen = SAMPLE_RANGE_IN_SEC * COLLECTION_FREQUENCY

if mode == ONLINE:
    init_func = init_online
    read_data_func = read_data_online
else:
    init_func = init_offline
    read_data_func = read_data_offline

def report_to_client(value):
    value = max(0,16-value+10)
    conn = httplib.HTTPConnection(APP_IP+":8080")
    thread.start_new_thread(conn.request, ("GET", "/set_user_state?value="+str(value)))
    print value

def start_monitoring():
    global analyse_func
    count = 0
    init_func()
    data = read_data_func()
    while data:
        count+=1
        sample_8_chan = struct.unpack(">iiiiiiii", data)
        for i in xrange(len(channelMatrix)):
            channelMatrix[i].insert(0,sample_8_chan[i])
            if len(channelMatrix[i])>sampleLen:
                analyse_func = do_marker
                channelMatrix[i].pop()
        #print channelMatrix
        data = read_data_func()
        if count%COLLECTION_FREQUENCY==0:
            count=0
            ret = analyse_func(channelMatrix)
            report_to_client(ret)
        
start_monitoring() 