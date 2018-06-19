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


class TestMechDriverPortChecks(base.NetworkingAnsibleTestCase):

    #######
    # Testing mech_driver._is_port_supported
    #######
    def test_is_port_supported(self):
        self.assertTrue(
            self.mech._is_port_supported(self.mock_port_context.current))

    def test_is_port_supported_not_baremetal(self):
        self.mock_port_context.current['binding:vnic_type'] = 'not-baremetal'
        self.assertFalse(
            self.mech._is_port_supported(self.mock_port_context.current))

    #######
    # Testing mech_driver._is_port_bound
    #######
    @mock.patch('networking_ansible.ml2.mech_driver.'
                'AnsibleMechanismDriver._is_port_supported')
    def test_is_port_bound(self, mock_port_supported):
        self.assertTrue(
            self.mech._is_port_bound(self.mock_port_context.current))

    @mock.patch('networking_ansible.ml2.mech_driver.'
                'AnsibleMechanismDriver._is_port_supported')
    def test_is_port_bound_not_other(self, mock_port_supported):
        self.mock_port_context.current['binding:vif_type'] = 'not-other'
        self.assertFalse(
            self.mech._is_port_bound(self.mock_port_context.current))

    @mock.patch('networking_ansible.ml2.mech_driver.'
                'AnsibleMechanismDriver._is_port_supported')
    def test_is_port_bound_port_not_supported(self, mock_port_supported):
        mock_port_supported.return_value = False
        self.assertFalse(
            self.mech._is_port_bound(self.mock_port_context.current))
