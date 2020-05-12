from node import Node
import json
import random
from pprint import pprint


class Client(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'CLIENT', hide_node=True)

        self.debug = False

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)


def main():
    client = Client(5, 9998)

    print('\nConnecting to Central Server ({}:{}) ......'.format(client.serverhost, 9999))

    _, data = client.connectandsend(client.serverhost, 9999, 'LNOD', '')[0]
    nodes = json.loads(data)

    print('Success! Find the following {} types of nodes:'.format(len(nodes)))

    for node_type in nodes:
        print('{}: {}'.format(node_type, nodes[node_type]['desc']))

    choices = [x for x in nodes]

    answer = input("Which type of nodes would you like to use [{}]: ".format('/'.join(choices))).upper()

    node = random.choice(nodes[answer]['nodes'])

    print('\nConnecting to {} Node ({}:{}) ......'.format(node['type'], node['ip'], node['port']))

    _, data = client.connectandsend(node['ip'], node['port'], 'LMET', '')[0]

    methods = json.loads(data)

    print('Success! Find the following {} methods:'.format(len(methods)))

    for msgtype in methods:
        print('{}: {}'.format(msgtype, methods[msgtype]['desc']))

    choices = [x for x in methods]

    answer = input("Which method would you like to use [{}]: ".format('/'.join(choices))).upper()

    inputs = {}

    if 'parameters' in methods[answer]:
        print('{} requires {} parameters:'.format(answer, len(methods[answer]['parameters'])))
        for key, details in methods[answer]['parameters'].items():
            inputs[key] = input('{}: '.format(details['text']))

    _, data = client.connectandsend(node['ip'], node['port'], answer, json.dumps(inputs))[0]

    pprint(data)


if __name__ == '__main__':
    main()

