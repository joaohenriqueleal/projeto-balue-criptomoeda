from network_protocol.handle import *


class Node:

    def __init__(self) -> None:
        self.broadcasts: 'Broadcasts' = Broadcasts()
        self.handle: 'Handle' = Handle()

    def peer_infos(self) -> None:
        print(f'IP public: {self.handle.public_ip}')
        print(f'IP local:  {self.handle.local_ip}')
        print(f'PORT:  {PORT}')
