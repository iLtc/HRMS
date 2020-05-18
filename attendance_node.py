from node import Node
import json
from datetime import datetime
import sqlite3


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)


class AttendanceNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'ATTENDANCE', node_desc='Handle User Clock in / out')

        self.debug = True

        self.addhandler('CLKI', self.__handle_clock_in)
        self.addhandler('CLKO', self.__handle_clock_out)
        self.addhandler('RQLV', self.__handle_request_leave)
        
        # self.addhandler(
        #     'STOT',
        #     self.__handle_show_totals,
        #     'show total numbers'
        #     )

        self.addhandler('REPT', self.__handle_report)

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def handle_list_method(self, method_name, data):
        if method_name == 'LMET':
            return True, '', None

        if data != '':
            data = json.loads(data)
        else:
            data = {'states': {}}

        if 'user_token' not in data['states']:
            return True, '', None

        if method_name == 'CLKI':
            return False, 'Allow user to clock in', None

        if method_name == 'CLKO':
            return False, 'Allow user to clock out', None

        if method_name == 'RQLV':
            return False, 'Allow user to request for leave', {
                'reason': {'text': 'Reason', 'required': True, 'type': 'textarea'}
            }

        if method_name == 'REPT':
            if data['states']['role'] == 'Employee':
                options = [{'text': data['states']['name'], 'value': data['states']['user_id']}]
            else:
                c = sqlite3.connect('database.db').cursor()

                options = [{'text': 'All', 'value': 'all'}]

                for user in c.execute('SELECT id, name FROM users'):
                    options.append({'text': user[1], 'value': user[0]})

            return False, 'Show the details of a specific user', {
                'id': {'text': 'User', 'required': True, 'type': 'select', 'options': options}
            }

        return True, '', None

    def __handle_clock_in(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        user_id = data['states']['user_id']

        now = datetime.now()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('INSERT INTO attendances (user_id, type, time, reason) VALUES (?, ?, ?, ?)', (user_id, 'Clock In', now, ''))

        conn.commit()

        peer_conn.senddata('CLKI', json.dumps(
            {'content': {'type': 'text', 'texts': ['Clock In Success!', 'You have clocked in at {}.'.format(now)]}}))

        # peer_conn.senddata('CLKI', json.dumps(res,cls=DateEncoder))

        self.peerlock.release()

    def __handle_clock_out(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        user_id = data['states']['user_id']

        now = datetime.now()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('INSERT INTO attendances (user_id, type, time, reason) VALUES (?, ?, ?, ?)', (user_id, 'Clock Out', now, ''))

        conn.commit()

        peer_conn.senddata('CLKO', json.dumps(
            {'content': {'type': 'text', 'texts': ['Clock Out Success!', 'You have clocked out at {}.'.format(now)]}}))

        # self.count -= 1
        # self.user_list[username]['clock_out_time'] = now

        self.peerlock.release()

    def __handle_request_leave(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        user_id = data['states']['user_id']

        reason = data['reason']
        now = datetime.now()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('INSERT INTO attendances (user_id, type, time, reason) VALUES (?, ?, ?, ?)', (user_id, 'Request Leave', now, reason))

        conn.commit()

        peer_conn.senddata('REQL', json.dumps(
            {'content': {'type': 'text', 'texts': ['Request Leave Success!', 'Your request has been added to the database.']}}))
        
        # self.user_list[username]['request_leave_time'] = now
        self.peerlock.release()

    # def __handle_show_totals(self, peer_conn, data):
    #     self.peerlock.acquire()
    #
    #     res = {"content": {'total attendance numbers': self.count, 'current_time':datetime.now()} }
    #     peer_conn.senddata('NUMS', json.dumps(res, cls=DateEncoder))
    #
    #     self.peerlock.release()

    def __handle_report(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        id_ = data['id']

        headers = ['ID', 'User Name', 'User Role', 'Type', 'Time', 'Reason']

        rows = []

        c = sqlite3.connect('database.db').cursor()

        if id_ == 'all':
            q = c.execute('SELECT attendances.id, name, role, "type", time, reason FROM users, attendances WHERE users.id = attendances.user_id')
        else:
            q = c.execute('SELECT attendances.id, name, role, "type", time, reason FROM users, attendances WHERE users.id = attendances.user_id AND user_id = ?', (id_, ))

        for row in q:
            rows.append([row[0], row[1], row[2], row[3], row[4], row[5]])

        response = {'content': {'type': 'table', 'headers': headers, 'rows': rows}}

        peer_conn.senddata('REPT', json.dumps(response))
        
        self.peerlock.release()


if __name__ == '__main__':
    an = AttendanceNode(5, 9003)

    an.mainloop()

