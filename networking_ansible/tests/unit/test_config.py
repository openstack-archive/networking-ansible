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

import mock

from networking_ansible.tests.unit import base


class MockedConfigParser(mock.Mock):

    def __init__(self, conffile, sections):
        super(MockedConfigParser, self).__init__()
        self.conffile = conffile
        self.sections = sections

    def parse(self):
        section_data = {'ansible:testhost': {'mac': ['01:23:45:67:89:ab']}}
        if self.conffile == 'foo2':
            section_data = {
                'ansible:h1': {'manage_vlans': ['0']},
                'ansible:h2': {'manage_vlans': ['true']},
                'ansible:h3': {'manage_vlans': ['false']},
            }

        self.sections.update(section_data)

    @staticmethod
    def _parse_file(values, namespace):
        pass


class TestConfig(base.BaseTestCase):
    parse_config = False

    def test_config_empty_hosts(self):
        self.test_config_files = []
        self.setup_config()

        self.assertEqual({}, self.ansconfig.Config().inventory)
        self.assertEqual({}, self.ansconfig.Config().mac_map)

    @mock.patch('networking_ansible.config.LOG')
    @mock.patch('networking_ansible.config.cfg.ConfigParser')
    def test_config_parser_error(self, mock_parser, mock_log):
        self.test_config_files = ['/etc/foo.conf']
        self.setup_config()

        mock_parser().parse.side_effect = IOError()
        self.assertEqual({}, self.ansconfig.Config().inventory)
        self.assertEqual({}, self.ansconfig.Config().mac_map)
        mock_log.error.assert_called()

    @mock.patch('networking_ansible.config.cfg.ConfigParser',
                MockedConfigParser)
    def test_config_w_hosts(self):
        self.test_config_files = ['foo']
        self.setup_config()

        self.assertEqual(self.m_config.inventory,
                         self.ansconfig.Config().inventory)
        self.assertEqual({'01:23:45:67:89:AB': 'testhost'},
                         self.ansconfig.Config().mac_map)

    @mock.patch('networking_ansible.config.cfg.ConfigParser',
                MockedConfigParser)
    def test_config_from_file(self):
        self.test_config_files = ['foo2']
        self.setup_config()

        hosts = self.ansconfig.Config().inventory
        self.assertEqual({'manage_vlans': False}, hosts['h1'])
        self.assertEqual({'manage_vlans': True}, hosts['h2'])
        self.assertEqual({'manage_vlans': False}, hosts['h3'])
        self.assertEqual({}, self.ansconfig.Config().mac_map)
