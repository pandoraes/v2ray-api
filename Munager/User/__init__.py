import json
import os,re
class User:
    def __init__(self, **entries):
        # for IDE hint
        self.user_id = None
        self.id = None
        self.email = None
        self.password = None
        self.uuid = None
        self.port = None
        self.method = None
        self.enable = None
        self.u = None
        self.d = None
        self.transfer_enable = None
        self.protocol = None
        self.protocol_param = None
        self.obfs = None
        self.obfs_param = None
        self.disconnect_ip = None
        self.prefixed_id = None
        self.__dict__.update(entries)
        self.available = self.if_available()
        if 'passwd' in self.__dict__:
            self.password = self.passwd
            self.__dict__.pop('passwd')

    def if_available(self):
        return not self.disconnect_ip

    def __str__(self):
        return json.dumps(self.__dict__)

class SS_user(User):
    def __init__(self, **entries):
        super(SS_user,self).__init__(**entries)
    def __eq__(self, other):
        return  other.password == self.password or \
        other.method == self.method or \
        other.id == self.id
    def get_InboundObject_json(self):
        pass

class Vmess_user(User):
    def __init__(self, **entries):
        super(Vmess_user,self).__init__(**entries)
    def __eq__(self, other):
        return other.id == self.id and other.alterId == self.alterId
    def set_alterId(self,alterId):
        self.alterId = alterId