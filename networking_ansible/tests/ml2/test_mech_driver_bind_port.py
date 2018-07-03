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

import unittest

import mock

from networking_ansible.tests import base


# TODO(radez) autospec seems to break things
@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.vlan_access_port')  # , autospec=True)
@mock.patch('networking_ansible.ml2.mech_driver.provisioning_blocks',
            autospec=True)
class TestMechDriverPortChecks(base.NetworkingAnsibleTestCase):
    def test_bind_port(self, mock_prov_blks, mock_vlan_access_port):
        self.mech.bind_port(self.mock_port_context)
        # TODO(radez) assert something
        mock_vlan_access_port.assert_called_once()

    @unittest.expectedFailure
    @mock.patch('networking_ansible.ml2.mech_driver.'
                'AnsibleMechanismDriver._is_port_supported', autospec=True)
    def test_bind_port_port_not_supported(self,
                                          mock_prov_blks,
                                          mock_vlan_access_port,
                                          mock_port_supported):
        # Error that results
        # File "networking_ansible/tests/ml2/test_mech_driver_bind_port.py",
        #                        line 37, in test_bind_port_port_not_supported
        #   self.mech.bind_port(self.mock_port_context)
        # File "networking_ansible/ml2/mech_driver.py", line 206, in bind_port
        #   if not (self._is_port_supported(port) and local_link_info):
        # TypeError: 'NonCallableMagicMock' object is not callable

        mock_port_supported.return_value = False
        self.mech.bind_port(self.mock_port_context)
        mock_vlan_access_port.assert_not_called()

    def test_bind_port_no_local_link_info(self,
                                          mock_prov_blks,
                                          mock_vlan_access_port):
        bind_prof = 'binding:profile'
        local_link_info = 'local_link_information'
        del self.mock_port_context.current[bind_prof][local_link_info]
        self.mech.bind_port(self.mock_port_context)
        mock_vlan_access_port.assert_not_called()
