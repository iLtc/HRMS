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

        self.addhandler('LIST', self.__handle_list, 'List all users in the database')

        self.addhandler(
            'DETA',
            self.__handle_details,
            'Show the details of a specific user',
            has_parameters=self.__handle_details_parameters)

        self.addhandler(
            'ADDU',
            self.__handle_add,
            'Add a user',
            has_parameters=self.__handle_add_parameters)

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def __handle_list(self, peer_conn, data):
        self.peerlock.acquire()

        results = ['{}\t{}'.format(str(user['id']), user['name']) for user in self.users]

        data = {'content': '\n'.join(results)}

        peer_conn.senddata('LISR', json.dumps(data))

        self.peerlock.release()

    def __handle_details_parameters(self, peer_conn, data):
        return {
            'id': {'text': 'User ID', 'required': True}
        }

    def __handle_details(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        results = [['{}: {}'.format(key, value) for key, value in user.items()] for user in self.users if user['id'] == data['id']]

        data = {'content': '\n'.join(results[0])}

        peer_conn.senddata('DETR', json.dumps(data))

        self.peerlock.release()

    def __handle_add_parameters(self, peer_conn, data):
        return {
            'id': {'text': 'User ID', 'required': True},
            'name': {'text': 'Name', 'required': True},
            'username': {'text': 'Username', 'required': True},
            'role': {'text': 'User Role', 'required': True}
        }

    def __handle_add(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        self.users.append(data)

        data = {'content': 'SUCCESS'}

        peer_conn.senddata('DETR', json.dumps(data))

        self.peerlock.release()


if __name__ == '__main__':
    un = UserNode(5, 9002)

    un.mainloop()

