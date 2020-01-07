#!/usr/bin/python3
import time
import rtmidi
import socket
from struct import pack

TCP_PORT = 8383
MIDI_PORT = "Midi2TCP"

def log(msg):
    print("{}: {}".format(MIDI_PORT, msg))

class MidiHandler(object):
    def __init__(self):
        self.socket = None

    def set_socket(self, sock):
        if self.socket is not None:
            self.socket.close()
        self.socket = sock

    def __call__(self, event, data):
        event, deltatime = event
        to_send = pack('<B%sB' % (len(event)), len(event), *event)
        if self.socket is not None:
            try:
                #log("Sending:L %r" % (event,))
                self.socket.send(to_send)
            except:
                self.socket.close()
                self.set_socket(None)
                log("Connection closed")
                raise
        #else:
            #log("Not sending:L %r" % to_send)

if __name__ == '__main__':
    midi = rtmidi.MidiIn()
    handler = MidiHandler()
    midi.set_callback(handler)
    device = midi.open_virtual_port(MIDI_PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', TCP_PORT))
    s.listen(10)

    try:
        while 1:
            log("Listening at port %d" % TCP_PORT)
            client = s.accept()
            log("Received connection from: %s" % (client[1],))
            handler.set_socket(client[0])

    finally:
        device.close_port()
