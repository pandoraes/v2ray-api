import json
import logging
from urllib.parse import urljoin, urlencode
from Munager.User import SS_user,Vmess_user
from .webapi_utils import WebApi
from configloader import load_config
class MuAPIError(Exception):
    pass

class MuAPI:
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = load_config()
        self.url_base = self.config.get('sspanel_url')
        self.key = self.config.get('key')
        self.node_id = self.config.get('node_id')
        self.webapi = WebApi()

    def get_users(self,key,node_info) -> dict:
        sort = node_info['sort']
        if sort==0:
            current_user = SS_user
            prifix = "SS_"
        else:
            current_user = Vmess_user
            prifix = "Vmess_"
            if node_info['server']['protocol']=="tcp":
                prifix+='tcp_'
            elif node_info['server']['protocol'] == 'ws':
                if node_info['server']['protocol_param']:
                    prifix+='ws_'+node_info['server']['protocol_param']+"_"
                else:
                    prifix += 'ws_' + "none" + "_"
            elif node_info['server']['protocol']=='kcp':
                if node_info['server']['protocol_param']:
                    prifix+='kcp_'+node_info['server']['protocol_param']+"_"
                else:
                    prifix += 'kcp_' + "none" + "_"
        try:
            data = self.webapi.getApi('users', {'node_id': self.node_id})
            ret = dict()
            for user in data:
                user['prefixed_id'] = prifix+user.get(key)
                user["user_id"] = user['id']
                user['id'] = user['uuid']
                ret[user['prefixed_id']] = current_user(**user)
                if 'Vmess' in prifix:
                    ret[user['prefixed_id']].set_alterId(int(node_info['server'].get('AlterId',16)))
            return ret
        except:
            return dict()

    def upload_throughput(self, data):
        """
        {'u': dt_transfer[id][0], 'd': dt_transfer[
                        id][1], 'user_id': uid}
        :param data:
        :return:
        """
        try:
            self.webapi.postApi('users/traffic',
                       {'node_id': self.node_id},
                       {'data': data})
            return True
        except:
            return False

    def upload_online_ips(self, data):
        try:
            self.webapi.postApi('users/aliveip',
                       {'node_id': self.node_id},
                       {'data': data})
            return True
        except:
            return False
    def upload_systemload(self):
        uptime = self.uptime()
        load = self.load()
        try:

            self.webapi.postApi(
                'nodes/%d/info' %
                (self.node_id), {
                    'node_id': self.node_id}, {
                    'uptime': str(
                        uptime), 'load': str(
                        load)})
            self.logger.info('upload_system load successed. uptime {}, load {}'.format(uptime, load))
        except:
            self.logger.info('upload_system load failed.')

    def get_node_info(self):
        try:
            data =self.webapi.getApi(
                'nodes/%d/info' %
                (self.node_id))
            temp_server = data['server'].split(";")
            server = dict(zip(["server_address", 'port', 'AlterId', 'protocol', 'protocol_param'], temp_server[:5]))
            # setting default
            if "protocol" not in server:
                server["protocol"] ="tcp"
            elif not server["protocol"]:
                server["protocol"] = "tcp"

            if "protocol_param" not in server:
                server["protocol_param"]=""
            if "protocol" in server:
                if server['protocol'] == "tls":
                    server['protocol'],server['protocol_param'] = server['protocol_param'] ,server['protocol']
            temp_extraArgs = []
            if len(temp_server)==6:
                temp_extraArgs = temp_server[5].split("|")
            extraArgs = {}
            for i in temp_extraArgs:
                if i:
                    key, value = i.split("=")
                    extraArgs[key] = value
            server['extraArgs'] = extraArgs
            data['server'] = server
            return data
        except:
            return None


    def uptime(self):
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])

    def load(self):
        import os
        return os.popen(
            "cat /proc/loadavg | awk '{ print $1\" \"$2\" \"$3 }'").readlines()[0]

