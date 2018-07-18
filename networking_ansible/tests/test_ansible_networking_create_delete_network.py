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

from networking_ansible.tests import base


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
