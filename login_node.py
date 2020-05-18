from node import Node
import json
import sqlite3
import sys


class LoginNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'LOGIN', node_desc='Handle User Login and Logout')

        self.debug = True

        self.addhandler('LOGI', self.__handle_login)
        self.addhandler('PASS', self.__handle_change_password)
        self.addhandler('PASU', self.__handle_change_password_user)
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

        if 'user_token' not in data['states']:
            return True, '', None

        if method_name == 'PASS':
            return False, 'Allow a user to change their password', {
                'opassword': {'text': 'Old Password', 'required': True, 'type': 'password'},
                'password': {'text': 'New Password', 'required': True, 'type': 'password'},
                'cpassword': {'text': 'Repeat Password', 'required': True, 'type': 'password'}
            }

        if method_name == 'PASU':
            if data['states']['role'] != 'Manager':
                return True, '', None

            c = sqlite3.connect('database.db').cursor()

            options = [{'text': '{} (ID: {})'.format(user[1], user[0]), 'value': user[0]} for user in c.execute('SELECT id, name FROM users WHERE id <> ?', (data['states']['user_id'], ))]

            return False, 'Allow a manager to change another user\'s password', {
                'id': {'text': 'User', 'required': True, 'type': 'select', 'options': options},
                'password': {'text': 'New Password', 'required': True, 'type': 'password'},
                'cpassword': {'text': 'Repeat Password', 'required': True, 'type': 'password'}
            }

        if method_name == 'LOGO':
            return False, 'Allow a user to logout', None

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

        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))

        result = c.fetchone()

        if result is None:
            peer_conn.senddata('LOGR', json.dumps(
                {'content': {'type': 'text', 'texts': ['Login Failed!', 'The username or password you entered does not match an account in our records!']}}))

        else:
            id_, name, username, password, role = result

            peer_conn.senddata('LOGR', json.dumps(
                {'content': {'type': 'text', 'texts': ['Login Success!', 'Welcome back, {}!'.format(name)]},
                 'states': {'name': name, 'user_token': username, 'role': role, 'user_id': id_}}))

        self.peerlock.release()

    def __handle_change_password(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        old_password = data['opassword']
        new_password = data['password']
        confirm_password = data['cpassword']

        conn = sqlite3.connect('database.db')

        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username=? AND password=?', (data['states']['user_token'], old_password))

        result = c.fetchone()

        if result is None:
            peer_conn.senddata('PASS', json.dumps(
                {'content': {'type': 'text', 'texts': ['Failed!', 'The old password you entered does not match our record!']}}))

        else:
            if new_password != confirm_password:
                response = {'content': {'type': 'text', 'texts': ['Error!', 'The two password fields don\'t match.']}}

            else:
                c.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, data['states']['user_id']))

                conn.commit()

                response = {'content': {'type': 'text', 'texts': ['Success!', 'The password has been changed', 'Please login again!']},
                            'states': {'name': None, 'user_token': None, 'role': None, 'user_id': None}}

            peer_conn.senddata('PASS', json.dumps(response))

        self.peerlock.release()

    def __handle_change_password_user(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        id_ = data['id']
        new_password = data['password']
        confirm_password = data['cpassword']

        conn = sqlite3.connect('database.db')

        c = conn.cursor()

        if new_password != confirm_password:
            response = {'content': {'type': 'text', 'texts': ['Error!', 'The two password fields don\'t match.']}}

        else:
            c.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, id_))

            conn.commit()

            response = {'content': {'type': 'text', 'texts': ['Success!', 'The password has been changed']}}

        peer_conn.senddata('PASU', json.dumps(response))

        self.peerlock.release()

    def __handle_logout(self, peer_conn, data):
        self.peerlock.acquire()

        peer_conn.senddata('LOGR', json.dumps(
            {'content': {'type': 'text', 'texts': ['Logout Success!', 'You have been logged out.']},
             'states': {'name': None, 'user_token': None, 'role': None, 'user_id': None}}))

        self.peerlock.release()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9001

    ln = LoginNode(5, port)

    ln.mainloop()

