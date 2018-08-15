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
from neutron.plugins.ml2.common import exceptions as ml2_exc


@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.create_network')
class TestMechDriverCreateNetworkPostCommit(base.NetworkingAnsibleTestCase):
    def setUp(self):
        super(TestMechDriverCreateNetworkPostCommit, self).setUp()

    def test_create_network_postcommit(self, mock_create_network):
        self.mech.create_network_postcommit(self.mock_net_context)
        mock_create_network.assert_called_once()

    def test_create_network_postcommit_manage_vlans_false(self,
                                                          mock_create_network):
        self.inventory['all']['hosts'][self.testhost]['manage_vlans'] = False
        self.mech.create_network_postcommit(self.mock_net_context)
        mock_create_network.assert_not_called()

    def test_create_network_postcommit_fails(self, mock_create_network):
        mock_create_network.side_effect = Exception()
        self.assertRaises(ml2_exc.MechanismDriverError,
                          self.mech.create_network_postcommit,
                          self.mock_net_context)
        mock_create_network.assert_called_once()

    def test_create_network_postcommit_not_vlan(self, mock_create_network):
        self.mock_net_context.current['provider:network_type'] = 'not-vlan'
        self.mech.create_network_postcommit(self.mock_net_context)
        mock_create_network.assert_not_called()

    def test_create_network_postcommit_not_segmentation_id(self,
                                                           mock_create_netwrk):
        self.mock_net_context.current['provider:segmentation_id'] = ''
        self.mech.create_network_postcommit(self.mock_net_context)
        mock_create_netwrk.assert_not_called()
