from connection.broadcasts.SendNodeInfos import *


class Broadcasts:

    def __init__(self) -> None:
        self.sni: 'SendNodeInfos' = SendNodeInfos()
