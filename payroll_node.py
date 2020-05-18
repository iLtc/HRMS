from node import Node
import json
import sqlite3


class PayrollNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'PAYROLL', node_desc='Handle User Payroll')

        self.debug = True

        self.addhandler('PAYS', self.__handle_payslips)
        self.addhandler('MODE', self.__handle_model)

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

        if method_name == 'PAYS':
            return False, 'Show all payslips', None

        if method_name == 'MODE':
            if data['states']['role'] != 'Manager':
                return True, '', None

            c = sqlite3.connect('database.db').cursor()

            models = {}

            for row in c.execute('SELECT role, salary FROM salary_models'):
                models[row[0]] = row[1]

            return False, 'Update the current payroll model', {
                'employee': {'text': 'Employee', 'required': True, 'type': 'text', 'value': models['Employee']},
                'supervisor': {'text': 'Supervisor', 'required': True, 'type': 'text', 'value': models['Supervisor']},
                'manager': {'text': 'Manager', 'required': True, 'type': 'text', 'value': models['Manager']}
            }

        return True, '', None

    def __handle_model(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.executemany('UPDATE salary_models SET salary = ? WHERE role = ?',
                      [(data['employee'], 'Employee'),
                       (data['supervisor'], 'Supervisor'),
                       (data['manager'], 'Manager')
                       ])

        conn.commit()

        response = {'content': {'type': 'text', 'texts': ['Update Success!', 'The new salary model has been saved.']}}

        peer_conn.senddata('MODE', json.dumps(response))

        self.peerlock.release()

    def __handle_payslips(self, peer_conn, data):
        self.peerlock.acquire()

        headers = ['Start Date', 'End Date', 'Hours', 'Amount']

        data = json.loads(data)

        c = sqlite3.connect('database.db').cursor()

        rows = []

        for row in c.execute('SELECT start, end, hours, amount FROM payslips WHERE user_id = ?', (data['states']['user_id'], )):
            rows.append([row[0], row[1], row[2], '$' + str(row[3])])

        response = {'content': {'type': 'table', 'headers': headers, 'rows': rows}}

        peer_conn.senddata('PAYS', json.dumps(response))

        self.peerlock.release()


if __name__ == '__main__':
    pn = PayrollNode(5, 9011)

    pn.mainloop()
