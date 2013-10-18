
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
        self.data_file.close()

brain_recorder = BrainRecorder()
brain_recorder.record()
