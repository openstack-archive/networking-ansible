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

from networking_ansible import exceptions
from networking_ansible.tests.unit import base


class MockedConfigParser(mock.Mock):
    def __init__(self, conffile, sections):
        super(MockedConfigParser, self).__init__()
        self.sections = sections

    def parse(self):
        self.sections.update({'ansible:testhost': {}})


class TestConfigBuildAnsibleInventory(base.NetworkingAnsibleTestCase):

    def test_build_ansible_inventory_empty_hosts(self):
        self.assertEqual(self.ansconfig.build_ansible_inventory(),
                         self.empty_inventory)

    @mock.patch('networking_ansible.config.LOG')
    @mock.patch('networking_ansible.config.cfg.ConfigParser')
    def test_build_ansible_inventory_parser_error(self, mock_parser, mock_log):
        mock_parser().parse.side_effect = IOError()
        self.assertEqual(self.ansconfig.build_ansible_inventory(),
                         self.empty_inventory)
        mock_log.error.assert_called()

    @mock.patch('networking_ansible.config.cfg.ConfigParser',
                MockedConfigParser)
    def test_build_ansible_inventory_w_hosts(self):
        self.assertEqual(self.ansconfig.build_ansible_inventory(),
                         self.inventory)


class TestAnsibleNetworkingCreateDeleteNetwork(base.NetworkingAnsibleTestCase):

    @mock.patch('networking_ansible.ansible_networking'
                '.AnsibleNetworking._run_task')
    def test_create_network(self, mock_run_task):
        self.mech.ansnet.create_network(self.testhost, self.testsegid)
        mock_run_task.assert_called_once_with('create_network',
                                              self.testhost,
                                              self.testsegid)

    @mock.patch('networking_ansible.ansible_networking'
                '.AnsibleNetworking._run_task')
    def test_delete_network(self, mock_run_task):
        self.mech.ansnet.delete_network(self.testhost, self.testsegid)
        mock_run_task.assert_called_once_with('delete_network',
                                              self.testhost,
                                              self.testsegid)


@mock.patch('networking_ansible.ansible_networking.ansible_runner')
class TestMechDriverRunTask(base.NetworkingAnsibleTestCase):
    def test_run_task_no_switchport(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   self.testsegid)
        # Assert switch_port is not set
        self.assertNotIn('port_name',
                         mock_ans_runner.run.call_args[1]['playbook'][0]
                                                      ['tasks'][0]['vars']
                         )
        # Assert switch_port is not set
        self.assertNotIn('port_description',
                         mock_ans_runner.run.call_args[1]['playbook'][0]
                                                      ['tasks'][0]['vars']
                         )

    def test_run_task_w_switchport(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   self.testsegid,
                                   'fake_switchport')
        # Assert switch_port is set
        self.assertEqual(
            'fake_switchport',
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['port_name'])
        # Assert switch_port is set
        self.assertEqual(
            'fake_switchport',
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['port_description'])

    def test_run_task_w_segmentation_id_1(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   '1',
                                   'fake_switchport')
        # Assert seg name is default
        self.assertEqual(
            'default',
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['segmentation_name'])

    def test_run_task_failures(self, mock_ans_runner):
        self.assertRaises(exceptions.AnsibleRunnerException,
                          self.mech.ansnet._run_task,
                          'fake_task',
                          self.testhost,
                          self.testsegid,
                          'fake_switchport')


@mock.patch('networking_ansible.ansible_networking'
            '.AnsibleNetworking._run_task')
class TestAnsibleNetworkingVlanAccessPort(base.NetworkingAnsibleTestCase):

    def test_assign_vlan_access_port(self, mock_run_task):
        self.mech.ansnet.vlan_access_port('assign',
                                          self.mock_port_context.current,
                                          self.mock_net_context.current)
        mock_run_task.assert_called_once_with('update_port',
                                              self.testhost,
                                              self.testsegid,
                                              self.testport)

    def test_remove_vlan_access_port(self, mock_run_task):
        self.mech.ansnet.vlan_access_port('remove',
                                          self.mock_port_context.current,
                                          self.mock_net_context.current)
        mock_run_task.assert_called_once_with('delete_port',
                                              self.testhost,
                                              self.testsegid,
                                              self.testport)

    def test_remove_vlan_access_port_wo_link_local(self, mock_run_task):
        port = self.mock_port_context.current
        del port['binding:profile']['local_link_information']
        self.mech.ansnet.vlan_access_port('remove',
                                          self.mock_port_context.current,
                                          self.mock_net_context.current)
        mock_run_task.assert_not_called()

    def test_remove_vlan_access_port_raises(self, mock_run_task):
        mock_run_task.side_effect = exceptions.AnsibleRunnerException('test')
        self.assertRaises(exceptions.AnsibleRunnerException,
                          self.mech.ansnet.vlan_access_port,
                          'remove',
                          self.mock_port_context.current,
                          self.mock_net_context.current)
