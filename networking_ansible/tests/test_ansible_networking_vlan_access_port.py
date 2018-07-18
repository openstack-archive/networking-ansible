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
from networking_ansible.tests import base


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
