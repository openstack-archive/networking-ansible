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

from mock import create_autospec
from mock import patch
from neutron.plugins.ml2 import driver_context

from networking_ansible.tests.base import AnsibleNetworkingTestCase


@patch('networking_ansible.ml2.mech_driver.AnsibleMechanismDriver.run_task')
class TestMechDriverCreateNetworkPostCommit(AnsibleNetworkingTestCase):
    def setUp(self):
        super(TestMechDriverCreateNetworkPostCommit, self).setUp()
        self.testhost = 'testhost'
        self.test_seg_id = '37'

    def test_create_network_postcommit(self, mock_run_task):
        self.mech.initialize()
        self.mech.inventory = {'all': {'hosts': {self.testhost: {}}}}

        mock_context = create_autospec(
                driver_context.NetworkContext).return_value
        mock_context.current = {'id': 37,
                                'provider:network_type': 'vlan',
                                'provider:segmentation_id': self.test_seg_id,
                                'provider:physical_network': 'physnet'}

        self.mech.create_network_postcommit(mock_context)
        mock_run_task.assert_called_once_with('create_network',
                                              self.testhost,
                                              self.test_seg_id)

    def test_create_network_postcommit_fails(self, mock_run_task):
        mock_run_task.side_effect = Exception()
        self.mech.initialize()
        self.mech.inventory = {'all': {'hosts': {'testhost': {}}}}

        mock_context = create_autospec(
                driver_context.NetworkContext).return_value
        mock_context.current = {'id': 37,
                                'provider:network_type': 'vlan',
                                'provider:segmentation_id': '37',
                                'provider:physical_network': 'physnet'}

        self.mech.create_network_postcommit(mock_context)
        mock_run_task.assert_called_once_with('create_network',
                                              self.testhost,
                                              self.test_seg_id)

    def test_create_network_postcommit_not_vlan(self, mock_run_task):
        self.mech.initialize()
        self.mech.inventory = {'all': {'hosts': {'testhost': {}}}}

        mock_context = create_autospec(
                driver_context.NetworkContext).return_value
        mock_context.current = {'id': 37,
                                'provider:network_type': 'not-vlan',
                                'provider:segmentation_id': '37',
                                'provider:physical_network': 'physnet'}

        self.mech.create_network_postcommit(mock_context)
        mock_run_task.assert_not_called()

    def test_create_network_postcommit_not_segmentation_id(self,
                                                           mock_run_task):
        self.mech.initialize()
        self.mech.inventory = {'all': {'hosts': {'testhost': {}}}}

        mock_context = create_autospec(
                driver_context.NetworkContext).return_value
        mock_context.current = {'id': 37,
                                'provider:network_type': 'vlan',
                                'provider:segmentation_id': '',
                                'provider:physical_network': 'physnet'}

        self.mech.create_network_postcommit(mock_context)
        mock_run_task.assert_not_called()
