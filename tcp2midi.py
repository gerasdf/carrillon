#!/usr/bin/python3
import time
import rtmidi
import socket
import select
from struct import pack,unpack

TCP_PORT  = 8384
MIDI_PORT = "TCP2Midi"

class TCPClient(object):
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
                print("Sending:L %r" % to_send)
                self.socket.send(to_send)
            except:
                self.socket.close()
                self.set_socket(None)
                print("Connection closed")
                raise
        else:
            print("Not sending:L %r" % to_send)

if __name__ == '__main__':
    midi = rtmidi.MidiOut()
    device = midi.open_virtual_port(MIDI_PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', TCP_PORT))
    s.listen(10)
    client_s = None

    try:
        print("Listening at port %d" % TCP_PORT)
        while 1:
            if client_s is not None:
                r = [s, client_s]
            else:
                r = [s]

            r,w,x = select.select(r,[],[])
            if s in r:
                if client_s:
                    client_s.close()
                    print("Connection forcefully closed (%s)" % (client_addr,))
                client_s, client_addr = s.accept()
                print("Received connection from: %s" % (client_addr, ))
            if client_s in r:
                count = client_s.recv(1)
                if not count:
                    print("Connection closed (%s)" % (client_addr,))
                    client_s.close()
                    client_s = None
                else:
                    count = unpack('B', count)[0]
                    print("Received %d bytes" % count)
                    data = client_s.recv(count)
                    if count == len(data):
                        data = unpack('{}B'.format(count), data)
                        print("Received %r" % (data,))
                        device.send_message(data)
                    else:
                        print("Received malformed data %r" % (data,))
    finally:
        device.close_port()