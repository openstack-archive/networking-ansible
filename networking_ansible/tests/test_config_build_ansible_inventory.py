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

from mock import patch

from networking_ansible.tests.base import AnsibleNetworkingTestCase


class TestConfigBuildAnsibleInventory(AnsibleNetworkingTestCase):

    def test_build_ansible_inventory_empty_hosts(self):
        self.config.build_ansible_inventory()

    @patch('oslo_config.cfg.ConfigParser')
    def test_build_ansible_inventory_parser_error(self, mock_configparser):
        mock_configparser().parse.side_effect = IOError()
        self.config.build_ansible_inventory()
