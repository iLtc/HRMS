from btpeer import *
import json


class Node(BTPeer):
    def __init__(self, max_peers, server_port, node_type, node_desc='', central_server_port=9999, hide_node=False):
        BTPeer.__init__(self, max_peers, server_port)

        self.debug = True

        self.node_type = node_type

        self.central_server_port = 9999

        self.addrouter(self.__router)

        self.addhandler('LMET', self.__handle_list_methods)

        if self.node_type != 'CENTRAL_SERVER':
            return_type, data = self.connectandsend(
                self.serverhost,
                central_server_port,
                'REGE',
                json.dumps({
                    'ip': self.serverhost,
                    'port': self.serverport,
                    'type': self.node_type,
                    'desc': node_desc,
                    'hide': hide_node
                })
            )[0]

            data = json.loads(data)

            self.node_id = data['id']

            self.__debug('Registered as node {}'.format(self.node_id))

    def __del__(self):
        if self.node_type != 'CENTRAL_SERVER':
            self.connectandsend(self.serverhost, self.central_server_port, 'UNRE', json.dumps({'id': self.node_id}))

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

    def __handle_list_methods(self, peer_conn, data):
        self.peerlock.acquire()

        methods = {}

        for msgtype in self.handlers:
            skip, desc, parameters = self.handle_list_method(msgtype, data)

            if skip:
                continue

            methods[msgtype] = {'msgtype': msgtype, 'desc': desc}

            if parameters is not None:
                methods[msgtype]['parameters'] = parameters

        peer_conn.senddata("LMER", json.dumps(methods))

        self.peerlock.release()

    def handle_list_method(self, method_name, data):
        return True, 'Not Implemented', None


if __name__ == '__main__':
    node = Node(5, 9123, 'TEST')
    # node.connectandsend('127.0.0.1', 9999, 'LNOD', '', waitreply=True)

