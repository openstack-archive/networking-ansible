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

from networking_ansible.tests.base import NetworkingAnsibleTestCase


class TestConfigBuildAnsibleInventory(NetworkingAnsibleTestCase):

    def test_build_ansible_inventory_empty_hosts(self):
        self.config.build_ansible_inventory()

    @patch('networking_ansible.config.cfg.ConfigParser.parse', autospec=True)
    def test_build_ansible_inventory_parser_error(self, mock_parse):
        mock_parse.side_effect = IOError()
        self.config.build_ansible_inventory
        # TODO(radez) assert something

    @patch('networking_ansible.config.cfg.ConfigParser.parse', autospec=True)
    @patch('builtins.dict.items')
    def test_build_ansible_inventory_w_hosts(self, mock_sections, mock_parse):
        mock_sections.return_value = {'ansible:testhost': 1}
        self.config.build_ansible_inventory()
