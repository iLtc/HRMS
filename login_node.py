from node import Node
import json
import sqlite3


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
                    'username': {'text': 'Username', 'required': True, 'type': 'text'},
                    'password': {'text': 'Password', 'required': True, 'type': 'password'}
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

        c = sqlite3.connect('database.db').cursor()

        t = (username, password)

        c.execute('SELECT * FROM users WHERE username=? AND password=?', t)

        result = c.fetchone()

        if result is None:
            peer_conn.senddata('LOGR', json.dumps(
                {'content': {'type': 'text', 'texts': ['Login Failed!', 'The username or password you entered does not match an account in our records!']}}))

        else:
            id_, name, username, password, role = result

            peer_conn.senddata('LOGR', json.dumps(
                {'content': {'type': 'text', 'texts': ['Login Success!', 'Welcome back, {}!'.format(name)]},
                 'states': {'name': name, 'user_token': username, 'role': role}}))

        self.peerlock.release()

    def __handle_logout(self, peer_conn, data):
        self.peerlock.acquire()

        peer_conn.senddata('LOGR', json.dumps(
            {'content': {'type': 'text', 'texts': ['Logout Success!', 'You have been logged out.']},
             'states': {'name': None, 'user_token': None, 'role': None}}))

        self.peerlock.release()


if __name__ == '__main__':
    ln = LoginNode(5, 9001)

    ln.mainloop()

