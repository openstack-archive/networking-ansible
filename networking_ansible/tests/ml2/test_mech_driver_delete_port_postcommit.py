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


@patch('networking_ansible.ml2.mech_driver.'
       'AnsibleMechanismDriver._is_port_bound')
@patch('networking_ansible.ansible_networking.'
       'AnsibleNetworking.vlan_access_port', autospec=True)
class TestMechDriverDeletePortPostCommit(NetworkingAnsibleTestCase):
    def test_delete_port_postcommit_current(self,
                                            mock_vlan_access,
                                            mock_port_bound):
        self.mech.delete_port_postcommit(self.mock_port_context)
        # TODO(radez) assert something

    def test_delete_port_postcommit_not_bound(self,
                                              mock_vlan_access,
                                              mock_port_bound):
        mock_port_bound.return_value = False
        self.mech.delete_port_postcommit(self.mock_port_context)
        # TODO(radez) assert something
