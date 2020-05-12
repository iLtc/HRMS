from node import Node
import json


class LoginNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'LOGIN', node_desc='Handle User Login and Logout')

        self.debug = True

        self.addhandler(
            'LOGI',
            self.__handle_login,
            'Allow a user to login',
            has_parameters=self.__handle_login_parameters
        )

        self.addhandler('LOGO', self.__handle_logout, 'Allow a user to logout')

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def __handle_login_parameters(self, peer_conn, data):
        return {
            'username': {'text': 'Username', 'required': True},
            'password': {'text': 'Password', 'required': True}
        }

    def __handle_login(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        username = data['username']
        password = data['password']

        if username == 'TEST' and password == 'PASS':
            peer_conn.senddata('LOGR', json.dumps({'content': 'SUCCESS'}))
        else:
            peer_conn.senddata('LOGR', json.dumps({'content': 'FAILED'}))

        self.peerlock.release()

    def __handle_logout(self, peer_conn, data):
        self.peerlock.acquire()

        peer_conn.senddata('LOGR', json.dumps({'content': 'SUCCESS'}))

        self.peerlock.release()


if __name__ == '__main__':
    ln = LoginNode(5, 9001)

    ln.mainloop()

