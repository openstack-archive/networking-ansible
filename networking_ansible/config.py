# Copyright (c) 2018 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
from oslo_config import types
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Config(object):

    driver_tag = 'ansible:'
    booleans = ['manage_vlans']

    def __init__(self):
        """Get inventory list from config files

        builds a Network-Runner inventory object
        and a mac_map dictionary
        according to ansible inventory file yaml definition
        http://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
        """
        self.inventory = {}
        self.mac_map = {}

        for conffile in CONF.config_file:
            # parse each config file
            sections = {}
            parser = cfg.ConfigParser(conffile, sections)
            try:
                parser.parse()
            except IOError as e:
                LOG.error(str(e))

            # filter out sections that begin with the driver's tag
            hosts = {k: v for k, v in sections.items()
                     if k.startswith(self.driver_tag)}

            # munge the oslo_config data removing the device tag and
            # turning lists with single item strings into strings
            for host in hosts:
                dev_id = host.partition(self.driver_tag)[2]
                dev_cfg = {k: v[0] for k, v in hosts[host].items()}
                for b in self.booleans:
                    if b in dev_cfg:
                        dev_cfg[b] = types.Boolean()(dev_cfg[b])
                self.inventory[dev_id] = dev_cfg
                # If mac is defined add it to the mac_map
                if 'mac' in dev_cfg:
                    self.mac_map[dev_cfg['mac'].upper()] = dev_id

        LOG.info('Ansible Host List: %s', ', '.join(self.inventory))
