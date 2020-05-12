from node import Node
import json
from pprint import pprint


class Client(Node):
    def __init__(self, max_peers, server_port, node_type, central_server_port=9999):
        Node.__init__(self, max_peers, server_port, node_type, central_server_port)

        self.debug = False

        self.node_type = node_type

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)


if __name__ == '__main__':
    # node = Node(5, 9000, 'TEST')
    # node.mainloop()
    # #
    client = Client(5, 9001, 'CLIENT')

    _, data = client.connectandsend('127.0.0.1', 9999, 'LNOD', '')[0]
    data = json.loads(data)
    pprint(data)

    _, data = client.connectandsend('127.0.0.1', 9999, 'LMET', '')[0]
    data = json.loads(data)
    pprint(data)

