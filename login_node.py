from node import Node
import json


class LoginNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'LOGIN', node_desc='Handle User Login and Logout')

        self.debug = True

        self.addhandler('LOGI', self.__handle_login)

        self.addhandler('LOGO', self.__handle_logout)

    def handle_list_method(self, method_name, data):
        if method_name == 'LMET':
            return True, '', None

        if data != '':
            data = json.loads(data)
        else:
            data = {'states': {}}

        if method_name == 'LOGI':
            if 'user_token' not in data['states']:
                return False, 'Allow a user to login', {
                    'username': {'text': 'Username', 'required': True},
                    'password': {'text': 'Password', 'required': True}
                }

            else:
                return True, '', None

        if method_name == 'LOGO':
            if 'user_token' in data['states']:
                return False, 'Allow a user to logout', None

            else:
                return True, '', None

        return True, '', None

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def __handle_login(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        username = data['username']
        password = data['password']

        if username == 'TEST' and password == 'PASS':
            peer_conn.senddata('LOGR', json.dumps({'content': 'SUCCESS', 'states': {'name': username, 'user_token': username, 'role': 'User'}}))
        else:
            peer_conn.senddata('LOGR', json.dumps({'content': 'FAILED'}))

        self.peerlock.release()

    def __handle_logout(self, peer_conn, data):
        self.peerlock.acquire()

        peer_conn.senddata('LOGR', json.dumps({'content': 'SUCCESS', 'states': {'name': None, 'user_token': None, 'role': None}}))

        self.peerlock.release()


if __name__ == '__main__':
    ln = LoginNode(5, 9001)

    ln.mainloop()

