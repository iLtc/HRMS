from node import Node
import json


class CentralServer(Node):
    def __init__(self, max_peers, server_port, node_type, central_server_port=9999):
        Node.__init__(self, max_peers, server_port, node_type, central_server_port)

        self.debug = True

        self.addhandler("REGE", self.__handle_register, "Register a new node", False)
        self.addhandler("UNRE", self.__handle_unregister, "Unregister a current node", True)
        self.addhandler("LNOD", self.__handle_list_node, "List all available nodes", False)

        self.node_index = 0
        self.available_nodes = {}

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def __handle_register(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        self.available_nodes[self.node_index] = {'ip': data['ip'], 'port': data['port'], 'type': data['type']}

        peer_conn.senddata("REGR", json.dumps({'id': self.node_index, 'status': 'success'}))

        self.__debug("A new node registered successfully! " + json.dumps(self.available_nodes[self.node_index]))

        self.node_index += 1

        self.peerlock.release()

    def __handle_unregister(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        del self.available_nodes[data['id']]

        self.__debug("Node {} has been unregistered.".format(data['id']))

        self.peerlock.release()

    def __handle_list_node(self, peer_conn, data):
        self.peerlock.acquire()

        peer_conn.senddata(
            "LNOR",
            json.dumps([{'id': id_,
                         'ip': data['ip'],
                         'port': data['port'],
                         'type': data['type']} for id_, data in self.available_nodes.items()]))

        self.peerlock.release()


if __name__ == '__main__':
    cs = CentralServer(5, 9999, 'CENTRAL_SERVER')
    cs.mainloop()
