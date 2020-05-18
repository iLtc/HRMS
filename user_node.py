from node import Node
import json
import sqlite3


class UserNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'USER', node_desc='Handle User Management')

        self.debug = True

        self.addhandler('LIST', self.__handle_list)

        self.addhandler('DETA', self.__handle_details)

        self.addhandler('ADDU', self.__handle_add)

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def handle_list_methods_msg(self, data, methods):
        if data != '':
            data = json.loads(data)
        else:
            data = {'states': {}}

        if 'user_token' not in data['states']:
            return 'You have not logged in yet! Please go to a LOGIN node to login first!'
        else:
            return super().handle_list_methods_msg(data, methods)

    def handle_list_method(self, method_name, data):
        if method_name == 'LMET':
            return True, '', None

        if data != '':
            data = json.loads(data)
        else:
            data = {'states': {}}

        if 'user_token' not in data['states']:
            return True, '', None

        if method_name == 'LIST':
            return False, 'List all users in the database', None

        if method_name == 'DETA':
            if data['states']['role'] == 'Employee':
                options = [{'text': data['states']['name'], 'value': data['states']['user_id']}]
            else:
                c = sqlite3.connect('database.db').cursor()

                options = [{'text': user[1], 'value': user[0]} for user in c.execute('SELECT id, name FROM users')]

            return False, 'Show the details of a specific user', {
                'id': {'text': 'User', 'required': True, 'type': 'select', 'options': options}
            }

        if method_name == 'ADDU':
            if data['states']['role'] != 'Manager':
                return True, '', None

            options = [
                {'text': 'Employee', 'value': 'Employee'},
                {'text': 'Supervisor', 'value': 'Supervisor'},
                {'text': 'Manager', 'value': 'Manager'}
            ]

            return False, 'Add a user', {
                'name': {'text': 'Name', 'required': True, 'type': 'text'},
                'username': {'text': 'Username', 'required': True, 'type': 'text'},
                'password': {'text': 'Password', 'required': True, 'type': 'password'},
                'cpassword': {'text': 'Repeat Password', 'required': True, 'type': 'password'},
                'role': {'text': 'User Role', 'required': True, 'type': 'select', 'options': options}
            }

        return True, '', None

    def __handle_list(self, peer_conn, data):
        self.peerlock.acquire()

        headers = ['User ID', 'User Name', 'User Role']

        c = sqlite3.connect('database.db').cursor()

        rows = [[user[0], user[1], user[2]] for user in c.execute('SELECT id, name, role FROM users')]

        data = {'content': {'type': 'table', 'headers': headers, 'rows': rows}}

        peer_conn.senddata('LISR', json.dumps(data))

        self.peerlock.release()

    def __handle_details(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        c = sqlite3.connect('database.db').cursor()

        c.execute('SELECT * FROM users WHERE id = ?', (data['id'],))

        result = c.fetchone()

        if result is None:
            peer_conn.senddata('DETR', json.dumps(
                {'content': {'type': 'text',
                             'texts': ['Error!', 'Cannot find the user with id = {}.'.format(data['id'])]}}))

        else:
            id_, name, username, password, role = result

            texts = ['User ID: ' + id_, 'User Name: ' + name, 'Username: ' + username, 'User Role: ' + role]

            data = {'content': {'type': 'text', 'texts': texts}}

            peer_conn.senddata('DETR', json.dumps(data))

        self.peerlock.release()

    def __handle_add(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        if 'states' in data:
            del data['states']

        if data['password'] != data['cpassword']:
            response = {'content': {'type': 'text', 'texts': ['Error!', 'The two password fields don\'t match.']}}
        else:
            conn = sqlite3.connect('database.db')

            c = conn.cursor()

            c.execute('INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)', (data['name'], data['username'], data['password'], data['role']))

            conn.commit()

            response = {'content': {'type': 'text', 'texts': ['User Add Success!', 'The new user has been added to the database.']}}

        peer_conn.senddata('DETR', json.dumps(response))

        self.peerlock.release()


if __name__ == '__main__':
    un = UserNode(5, 9010)

    un.mainloop()
