#!/usr/bin/env python3
import socket
import logging

SERVER_URL = 'localhost'
SERVER_PORT = 1452
BUF_SIZE = 4096


class ExampleBot:
    def __init__(self, host, port):
        # Join a game
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.in_buf = self.sock.makefile('rb', BUF_SIZE)
        self.out_buf = self.sock.makefile('wb', BUF_SIZE)

        # Receive welcome message
        self.parse_welcome()

    def parse_welcome(self):
        '''
        Receive the welcome message, parse all info in it and start playing
        '''
        logging.info('Welcome message: ' + self.recv_msg())
        self.send_msg('bla back')
        self.playing = True

    def play(self):
        '''
        Infinitely play the game. Figure out the next move(s), parse incoming
        data, try to win :)
        '''
        while self.playing:
            cmds = self.determine_commands()
            for cmd in cmds:
                self.sock.send(cmd + '\n')

    def determine_commands(self):
        '''
        The heart of the AI of the robot. If you implement anything, implement
        this, and please don't just let it drive around for half an hour, then
        blow itself up.
        '''
        cmds = []
        # Think of move
        # Think of fire
        # Think of scan
        return cmds

    def recv_msg(self):
        '''
        Utility function to retrieve a message
        '''
        line = self.in_buf.readline().decode('utf-8').strip()
        return line

    def send_msg(self, msg):
        '''
        Utility function to send a message
        '''
        self.out_buf.write(bytes(msg if msg.endswith('\n') else msg + '\n',
            'utf-8'))
        self.out_buf.flush()


def main():
    logging.basicConfig(format='%(asctime)s [ %(levelname)7s ] : %(message)s',
            level=logging.INFO)

    bot = ExampleBot(SERVER_URL, SERVER_PORT)
    bot.play()

if __name__ == '__main__':
    main()
