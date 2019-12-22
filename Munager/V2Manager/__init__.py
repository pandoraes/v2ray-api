import time
from Munager.V2Manager.client import *
from Munager.V2Manager.errors import *
import uuid
import os
from configloader import  load_config
from copy import deepcopy

class V2Manager:
    def __init__(self,current_node_info=None, next_node_info=None):
        self.config = load_config()
        self.logger = logging.getLogger()
        self.client = Client("127.0.0.1", self.config.get("api_port","2333"))
        self.current_node_info = current_node_info
        self.next_node_info = next_node_info
        self.if_user_change = False
        self.logger.info('Manager initializing.')
        self.INBOUND_TAG = "MAIN_INBOUND"
        self.users_to_be_removed = {}
        self.users_to_be_add = {}
        self.current_inbound_tags = set()
        self.users = {}
        if not self.config.get("docker",False):
            self.restart()

    def get_users(self):

        return self.users

    def add(self, user):
        self.if_user_change = True
        self.users_to_be_add[user.prefixed_id] = user
        return True

    def remove(self, prefixed_id):
        if prefixed_id in self.users:
            user = self.users[prefixed_id]
            self.if_user_change = True
            self.users_to_be_removed[user.prefixed_id] = user
            return True
        else:
            return False

    def update_users(self):
        successfully_removed = []
        successfully_add = []
        if self.current_node_info:
            if self.current_node_info['sort'] == 0:
                # SS server
                # remove users
                for prefixed_id in self.users_to_be_removed:
                    try:
                        self.client.remove_inbound(prefixed_id)
                        logging.info("Successfully remove user {}".format(prefixed_id))
                    except InboundNotFoundError:
                        logging.info(
                            "not enough information for making a decision or {} has been removed".format(prefixed_id))
                        successfully_removed.append(prefixed_id)
                    except V2RayError as e:
                        logging.warning(e.details)
                    else:
                        successfully_removed.append(prefixed_id)

            elif self.current_node_info['sort'] == 11:
                ## VMESS
                ## Remove users
                for prefixed_id in self.users_to_be_removed:
                    user = self.users_to_be_removed[prefixed_id]
                    try:
                        self.client.remove_user(inbound_tag=self.INBOUND_TAG, email=user.email)
                        logging.info("Successfully remove user {}".format(user.prefixed_id))
                    except EmailNotFoundError:
                        logging.info("NOt find the user {}".format(user.prefixed_id))
                        successfully_removed.append(prefixed_id)
                    except InboundNotFoundError:
                        logging.info("Successfully remove user {}".format(user.prefixed_id))
                        successfully_removed.append(prefixed_id)
                    except V2RayError as e:
                        logging.warning(e.details)
                    else:
                        successfully_removed.append(prefixed_id)

        time.sleep(5)
        if self.next_node_info:
            if self.next_node_info['sort'] == 0:
                # add users
                for prefixed_id in self.users_to_be_add:
                    user = self.users_to_be_add[prefixed_id]
                    try:
                        proxy = SSInbound(user)
                        self.client.add_inbound(tag=user.prefixed_id, address="0.0.0.0", port=int(user.port),
                                                proxy=proxy)
                    except AddressAlreadyInUseError:
                        logging.info("Port already in use, user {}, port {}".format(user.prefixed_id, user.port))
                        successfully_add.append(prefixed_id)
                    except V2RayError as e:
                        logging.warning(e.details)
                    else:
                        logging.info("Successfully add user {}".format(user.prefixed_id))
                        successfully_add.append(prefixed_id)
            elif self.next_node_info['sort'] == 11:
                # Add users
                for prefixed_id in self.users_to_be_add:
                    user = self.users_to_be_add[prefixed_id]
                    try:
                        self.client.add_user(inbound_tag=self.INBOUND_TAG, user_id=user.uuid, email=user.email, level=0,
                                             alter_id=user.alterId)

                    except EmailExistsError:
                        logging.info("Email exist")
                        successfully_add.append(prefixed_id)
                    except InboundNotFoundError:
                        logging.info("Inbound not found")
                    except V2RayError as e:
                        logging.warning(e.details)
                    else:
                        successfully_add.append(prefixed_id)
                        logging.info("Successfully add user {}".format(user.prefixed_id))

        for prefixed_id in successfully_removed:
            self.users.pop(prefixed_id)
            self.users_to_be_removed.pop(prefixed_id)
        for prefixed_id in successfully_add:
            self.users[prefixed_id] = self.users_to_be_add.pop(prefixed_id)

    def update_server(self):
        self.users_to_be_removed = deepcopy(self.users)
        self.users_to_be_add = {}
        self.update_users()
        self.remove_inbounds()
        self.add_main_inbound()
        self.users =dict()

    def update_main_address_and_prot(self, node_info):
        if node_info['sort'] == 11:
            if node_info['server'].get('port', '443') == '443':
                self.main_listen_address = '127.0.0.1'
                self.main_listen_port = int(node_info['server']['extraArgs'].get('inside_port', "10550"))
            else:
                self.main_listen_address = '0.0.0.0'
                self.main_listen_port = int(node_info['server'].get('port', '443'))

    def add_main_inbound(self):
        # only for VMESS
        if self.next_node_info:
            if self.next_node_info['sort'] == 11:
                self.update_main_address_and_prot(self.next_node_info)
                vmess = VMessInbound(
                    [{
                        'email': 'rico93@example.com',
                        'level': 0,
                        'alterId': 16,
                        'uuid': uuid.uuid4().hex
                    }
                    ]
                )
                steamsetting = StreamSetting()
                if self.next_node_info['server'].get("protocol", "tcp") == "ws":
                    host = None
                    path = None
                    extraArgs = self.next_node_info['server'].get("extraArgs", {})
                    if extraArgs:
                        path = extraArgs.get('path', '/')
                        host = extraArgs.get('host', "www.google.com")
                    if path and host:
                        steamsetting = Websocket(path=path, host=host)
                    else:
                        steamsetting = Websocket()
                elif self.next_node_info['server'].get("protocol", "tcp") == "kcp":
                    header_key = self.next_node_info['server'].get("protocol_param", 'noop')
                    steamsetting = Kcp(header_key=header_key)
                try:
                    self.client.add_inbound(tag=self.INBOUND_TAG, address=self.main_listen_address,
                                            port=self.main_listen_port,
                                            proxy=vmess, streamsetting=steamsetting.streamconfig)
                except AddressAlreadyInUseError:
                    logging.info("Port already in use, {}".format(self.INBOUND_TAG, self.main_listen_port))
                except V2RayError as e:
                    logging.warning(e.details)
                else:
                    logging.info(
                        "Successfully add MAIN INBOUND {} port {}".format(self.INBOUND_TAG, self.main_listen_port))

    def remove_inbounds(self):
        if self.current_node_info:
            if self.current_node_info['sort'] == 11:
                self.update_main_address_and_prot(self.current_node_info)
                try:
                    self.client.remove_inbound(tag=self.INBOUND_TAG)
                    logging.info("Successfully remove main inbound {}".format(self.INBOUND_TAG))
                except InboundNotFoundError:
                    logging.info(
                        "not enough information for making a decision")
                except V2RayError as e:
                    logging.warning(e.details)
            else:
                logging.info("ss user will be remove later")
        else:
            logging.info("No main Inbound currently! ")

    def restart(self):
        self.logger.info("Restart V2ray Service")
        service_name = ["v2ray", "nginx", "httpd", "apache2"]
        if not self.config.get("docker", False):
            start_cmd = "service {} start >/dev/null 2>&1"
            stop_cmd = "service {} stop >/dev/null 2>&1"
            status_cmd = "service {} status >/dev/null 2>&1"
        else:
            start_cmd = "/etc/init.d/{} start >/dev/null 2>&1"
            stop_cmd = "/etc/init.d/{} stop >/dev/null 2>&1"
            status_cmd = "/etc/init.d/{} status >/dev/null 2>&1"
        os.system(stop_cmd.format("v2ray"))
        os.system(start_cmd.format("v2ray"))

        result = os.system(status_cmd.format('v2ray'))
        if result != 768:
            self.logger.info("v2ray running !!!")
        else:
            self.logger.warning("There is something wrong, v2ray didn't run service")

