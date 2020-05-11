from btpeer import *


class Node(BTPeer):
    def __init__(self, max_peers, server_port, node_type, central_server_port=9999):
        BTPeer.__init__(self, max_peers, server_port)

        self.debug = True

        self.node_type = node_type

        self.addrouter(self.__router)

    def __debug(self, msg):
        if self.debug:
            btdebug(msg)

    def __router(self, peer_id):
        if peer_id not in self.getpeerids():
            return None, None, None
        else:
            rt = [peer_id]
            rt.extend(self.peers[peer_id])
            return rt


if __name__ == '__main__':
    # node = Node(5, 9000, 'TEST')
    # node.mainloop()
    # #
    node = Node(5, 9001, 'TEST')
    node.connectandsend('127.0.0.1', 9000, 'TEST', 'haha')
    node.connectandsend()

