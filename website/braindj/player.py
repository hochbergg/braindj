# import win32com.client
import subprocess
import time

class Player(object):
    def start_song(self):
        pass
    def next_song(self):
        pass
    def get_current_song(self):
        pass
    def pause(self):
        pass


class MacItunesPlayer(Player):
    OSASCRIPT_PATH = '/usr/bin/osascript'
    AVILABE_CMDS = ['play', 'pause', 'next track', 'previous track',
                    'set mute to true', 'set mute to false', 
                    'player state as string',
                    'artist of current track as string',
                    'name of current track as string',
                    'stop', 'quit']

    def __init__(self):
        self.playing = False
        self.start_time = 0

    def get_currently_song_time(self):
        """
        in seconds
        """
        return int(time.time() - self.start_time)

    def start_song(self):
        self._run_cmd("play")
        self.start_time = time.time()

    def next_song(self):
        self._run_cmd("next track")

    def get_current_song(self):
        return "%s - %s" % (self.get_artist().strip(), self.get_song_name().strip())

    def get_artist(self):
        return self._run_cmd('artist of current track as string').stdout.read()

    def get_song_name(self):
        return self._run_cmd('name of current track as string').stdout.read()

    def pause(self):
        self._run_cmd("pause")

    @classmethod
    def _run_cmd(cls, cmd):
        """
        gets a command to put in osascript -e ...
        """
        if cmd not in cls.AVILABE_CMDS:
            raise ValueError("cmd not available")

        sub = subprocess.Popen("""%s -e 'tell application "iTunes" to %s'""" % (cls.OSASCRIPT_PATH, cmd), 
                    shell=True, stdin=subprocess.PIPE, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return sub


class WinItunesPlayer(Player):
    def __init__(self):
        import win32com.client
        self.itunes = win32com.client.Dispatch("iTunes.Application")

    def get_current_song(self):    
        # self.itunes.CurrentTrack. (artists?)
        return self.itunes.CurrentTrack.Name

    def pause(self):
        self.itunes.Pause()

    def start_song(self):
        self.itunes.Play()

    def next_song(self):
        self.itunes.Pause()
        self.itunes.NextTrack()

    def close(self):
        self.itunes.Quit()

