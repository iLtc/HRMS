from node import Node
import json


class UserNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'USER', node_desc='Handle User Management')

        self.debug = True

        self.users = [
            {'id': '1', 'name': 'Person A', 'username': 'PA', 'role': 'Employee'},
            {'id': '2', 'name': 'Person B', 'username': 'PB', 'role': 'Employee'},
            {'id': '3', 'name': 'Person C', 'username': 'PC', 'role': 'Employee'}
        ]

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
            options = [{'text': user['name'], 'value': user['id']} for user in self.users]

            return False, 'Show the details of a specific user', {
                'id': {'text': 'User', 'required': True, 'type': 'select', 'options': options}
            }

        if method_name == 'ADDU':
            options = [
                {'text': 'Employee', 'value': 'Employee'},
                {'text': 'Supervisor', 'value': 'Supervisor'},
                {'text': 'Manager', 'value': 'Manager'}
            ]

            return False, 'Add a user', {
                'id': {'text': 'User ID', 'required': True, 'type': 'text'},
                'name': {'text': 'Name', 'required': True, 'type': 'text'},
                'username': {'text': 'Username', 'required': True, 'type': 'text'},
                'role': {'text': 'User Role', 'required': True, 'type': 'select', 'options': options}
            }

        return True, '', None

    def __handle_list(self, peer_conn, data):
        self.peerlock.acquire()

        headers = ['User ID', 'User Name']

        rows = [[user['id'], user['name']] for user in self.users]

        data = {'content': {'type': 'table', 'headers': headers, 'rows': rows}}

        peer_conn.senddata('LISR', json.dumps(data))

        self.peerlock.release()

    def __handle_details(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        results = [['{}: {}'.format(key, value) for key, value in user.items()] for user in self.users if user['id'] == data['id']]

        data = {'content': {'type': 'text', 'texts': results[0]}}

        peer_conn.senddata('DETR', json.dumps(data))

        self.peerlock.release()

    def __handle_add(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        if 'states' in data:
            del data['states']

        self.users.append(data)

        data = {'content': {'type': 'text', 'texts': ['User Add Success!', 'The new user has been added to the database.']}}

        peer_conn.senddata('DETR', json.dumps(data))

        self.peerlock.release()


if __name__ == '__main__':
    un = UserNode(5, 9002)

    un.mainloop()

