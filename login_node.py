from node import Node
import json


class LoginNode(Node):
    def __init__(self, max_peers, server_port, node_type, central_server_port=9999):
        Node.__init__(self, max_peers, server_port, node_type, central_server_port)

        self.debug = True

        self.node_type = node_type

        self.addhandler('LOGI', self.__handle_login, 'Allow a user to login', True)
        self.addhandler('LOGO', self.__handle_logout, 'Allow a user to logout', False)

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def __handle_login(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        username = data['username']
        password = data['password']

        if username == 'TEST' and password == 'PASS':
            peer_conn.senddata('LOGR', json.dumps({'result': 'SUCCESS'}))
        else:
            peer_conn.senddata('LOGR', json.dumps({'result': 'FAILED'}))

        self.peerlock.release()

    def __handle_logout(self, peer_conn, data):
        pass


if __name__ == '__main__':
    ln = LoginNode(5, 9001, 'LOGIN')

    ln.mainloop()

