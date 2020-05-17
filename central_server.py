from node import Node
import json


class CentralServer(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'CENTRAL_SERVER', 9999)

        self.debug = True

        self.addhandler("REGE", self.__handle_register)
        self.addhandler("UNRE", self.__handle_unregister)
        self.addhandler("LNOD", self.__handle_list_node)

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

        if data['id'] in self.available_nodes:
            del self.available_nodes[data['id']]

        self.__debug("Node {} has been unregistered.".format(data['id']))

        self.peerlock.release()

    def __handle_list_node(self, peer_conn, data):
        self.peerlock.acquire()

        nodes = {}

        for id_, node in self.available_nodes.items():
            if node['hide']:
                continue

            if node['type'] not in nodes:
                nodes[node['type']] = {'desc': node['desc'], 'nodes': []}

            nodes[node['type']]['nodes'].append({'id': id_,
                                                 'ip': node['ip'],
                                                 'port': node['port'],
                                                 'type': node['type'],
                                                 'desc': node['desc']})

        data = json.loads(data)

        if 'name' in data['states']:
            msg = "Hello, {}! Welcome to HRMS! <br> We found the following {} types of node you can use:".format(data['states']['name'], len(nodes))

        else:
            msg = "Hello! Welcome to HRMS! Please go to a LOGIN node to login first. <br> We found the following {} types of node you can use:".format(len(nodes))

        peer_conn.senddata("LNOR", json.dumps({'msg': msg, 'nodes': nodes}))

        self.peerlock.release()


if __name__ == '__main__':
    cs = CentralServer(5, 9999)
    cs.mainloop()
