from node import Node
import json


class CentralServer(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'CENTRAL_SERVER', 9999)

        self.debug = True

        self.addhandler("REGE", self.__handle_register, "Register a new node")
        self.addhandler("UNRE", self.__handle_unregister, "Unregister a current node")
        self.addhandler("LNOD", self.__handle_list_node, "List all available nodes")

        self.node_index = 0
        self.available_nodes = {}

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def __handle_register(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        self.available_nodes[self.node_index] = {
            'ip': data['ip'],
            'port': data['port'],
            'type': data['type'],
            'desc': data['desc'],
            'hide': data['hide']
        }

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

        nodes = {}

        for id_, data in self.available_nodes.items():
            if data['hide']:
                continue

            if data['type'] not in nodes:
                nodes[data['type']] = {'desc': data['desc'], 'nodes': []}

            nodes[data['type']]['nodes'].append({'id': id_,
                                                 'ip': data['ip'],
                                                 'port': data['port'],
                                                 'type': data['type'],
                                                 'desc': data['desc']})

        peer_conn.senddata("LNOR", json.dumps(nodes))

        self.peerlock.release()


if __name__ == '__main__':
    cs = CentralServer(5, 9999)
    cs.mainloop()
