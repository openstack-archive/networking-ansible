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


# Cannot call with autospec=True, the resulting mock object doesn't
# include the function assert_called_once_with
@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.delete_network')
class TestMechDriverDeleteNetworkPostCommit(base.NetworkingAnsibleTestCase):
    def setUp(self):
        super(TestMechDriverDeleteNetworkPostCommit, self).setUp()

    def test_delete_network_postcommit(self, mock_delete_network):
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_called_once_with(self.testhost,
                                                    self.testsegid)

    def test_delete_network_postcommit_manage_vlans_false(self,
                                                          mock_delete_network):
        self.inventory['all']['hosts'][self.testhost]['manage_vlans'] = False
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_not_called()

    def test_delete_network_postcommit_fails(self, mock_delete_network):
        mock_delete_network.side_effect = Exception()
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_called_once_with(self.testhost,
                                                    self.testsegid)

    def test_delete_network_postcommit_not_vlan(self, mock_delete_network):
        self.mock_net_context.current['provider:network_type'] = 'not-vlan'
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_not_called()

    def test_delete_network_postcommit_not_segmentation_id(self,
                                                           mock_delete_netwrk):
        self.mock_net_context.current['provider:segmentation_id'] = ''
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_netwrk.assert_not_called()
