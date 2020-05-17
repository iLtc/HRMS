from node import Node
import json
from datetime import datetime
from collections import defaultdict

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)

class AttendanceNode(Node):
    def __init__(self, max_peers, server_port):
        Node.__init__(self, max_peers, server_port, 'ATTEND', node_desc='Handle User Clock in / out')

        self.debug = True

        self.count = 0
        self.user_list = defaultdict(dict)

        self.addhandler(
            'CLKI',
            self.__handle_clock_in,
            'user clock in',
            has_parameters=self.__handle_clock_parameters
        )

        self.addhandler(
            'CLKO',
            self.__handle_clock_out,
            'user clock out',
            has_parameters=self.__handle_clock_parameters
            )
        
        self.addhandler(
            'RQLV',
            self.__handle_request_leave,
            'user request for leave',
            has_parameters=self.__handle_clock_parameters
            )
        
        self.addhandler(
            'STOT',
            self.__handle_show_totals,
            'show total numbers'
            )

        self.addhandler(
            'REPT',
            self.__handle_report,
            'show user report'
            )

    def __debug(self, msg):
        if self.debug:
            self.btdebug(msg)

    def __handle_clock_parameters(self, peer_conn, data):
        return {
            'username': {'text': 'Username', 'required': True}
        }

    def __handle_clock_in(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        username = data['username']

        now = datetime.now()

        res = {"content": {'user': username,'clock_in_time': now} }
        peer_conn.senddata('CLKI', json.dumps(res,cls=DateEncoder))

        self.count += 1

        self.user_list[username]["clock_in_time"] = now

        self.peerlock.release()

    def __handle_clock_out(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        username = data['username']

        now = datetime.now()
        res = {"content": {'user': username,'clock_out_time':now}}
        peer_conn.senddata('CLKO', json.dumps(res,cls=DateEncoder))

        self.count -= 1
        self.user_list[username]['clock_out_time'] = now

        self.peerlock.release()

    def __handle_request_leave(self, peer_conn, data):
        self.peerlock.acquire()

        data = json.loads(data)

        username = data['username']
        now = datetime.now()
        res = {"content": {'user': username,'request_leave_time':now}}
        peer_conn.senddata('REQL', json.dumps(res,cls=DateEncoder))
        
        self.user_list[username]['request_leave_time'] = now
        self.peerlock.release()


    def __handle_show_totals(self, peer_conn, data):
        self.peerlock.acquire()

        res = {"content": {'total attendance numbers': self.count, 'current_time':datetime.now()} }
        peer_conn.senddata('NUMS', json.dumps(res, cls=DateEncoder))
        
        self.peerlock.release()

    def __handle_report(self, peer_conn, data):
        self.peerlock.acquire()

        res = {"content": self.user_list}
        peer_conn.senddata('REPT', json.dumps(res, cls=DateEncoder))
        
        self.peerlock.release()


if __name__ == '__main__':
    an = AttendanceNode(5, 9003)

    an.mainloop()

