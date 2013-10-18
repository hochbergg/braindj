##import win32com
import win32com.client
import socket
import time
import thread

# connect to itunes
# start recording

SERVER_IP = "172.20.10.9"

class BrainRecorder(object):
    def __init__(self):
        self.keep_recording = True
        self.data_file = open("recording_{}.bin".format(time.asctime().replace(":","_")),'wb')
        self.client = socket.socket(socket.AF_INET)
    def record(self):
        print "hi"
        self.client.connect((SERVER_IP,1234))
        print "connected"
        while self.keep_recording:
            data = self.client.recv(1024)
            if len(data) == 0:
                self.data_file.close()
                raise Exception("Connection closed")
            self.data_file.write(data)
    def stop_recording(self):
        self.keep_recording = False
        time.sleep(1)
        self.data_file.close()


class Listener():
    def __init__(self):
        self.log_file = open("log_{}.txt".format(time.asctime().replace(":","_")),'wb')
        self.log_file.write("Start\t{}\t{}\n".format(time.asctime(),time.time()))
        self.itunes = win32com.client.Dispatch("iTunes.Application")
    def synchronization(self):
        print "Byte your teeth in"
        time.sleep(1)
        print "3..."
        time.sleep(1)
        print "2..."
        time.sleep(1)
        print "1..."
        time.sleep(1)
        print "NOW!"
        self.log_file.write("Teethbyte\t{}\t{}\n".format(time.asctime(),time.time()))
    def stop_listening(self):
        self.log_file.write("Stopped\t{}\t{}\n".format(time.asctime(),time.time()))
        self.itunes.Pause()
        self.log_file.close()
    def start_song(self):
        self.itunes.Play()
        self.log_file.write("Songstart\t{} played on {}\t{}\n".format(self.itunes.CurrentTrack.Name,time.asctime(),time.time()))
    def next_song(self):
        self.itunes.Pause()
        self.log_file.write("Songpassed\t{}\ton {}\t{}\n".format(self.itunes.CurrentTrack.Name,time.asctime(),time.time()))
        self.itunes.NextTrack()
    def feedback(self):
        print "Are you enjoying the song? (y/n)"
        inp = raw_input()
        self.log_file.write("Enjoyment\t{}\t{}\t{}\t{}\n".format(self.itunes.CurrentTrack.Name,inp,time.asctime(),time.time()))
    def iteration(self):
        self.start_song()
        self.feedback()
        print "Press any key for next song or q to stop..."
        a = raw_input()
        if a!='q':
            self.next_song()
            return True
        else:
            self.next_song()
            return False

brain_recorder = BrainRecorder()
print "Press any key to start recording"
raw_input()
thread.start_new_thread(brain_recorder.record,())
l = Listener()
l.synchronization()
l.synchronization()
l.synchronization()
a = True
while a:
    a = l.iteration()
l.itunes.Pause()
l.synchronization()
l.synchronization()
l.synchronization()
l.stop_listening()
print "Sleeping for 3 minutes to make sure all the data is transfered..."
time.sleep(3*60)
brain_recorder.stop_recording()

##print "Press any key to play song..."
##raw_input()
### play
##itunes.Play()


# ask questions
# pause
# track next

