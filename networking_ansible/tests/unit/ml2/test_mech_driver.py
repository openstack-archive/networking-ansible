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

from neutron.plugins.ml2.common import exceptions as ml2_exc

from networking_ansible.tests.unit import base


@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.vlan_access_port')
@mock.patch('networking_ansible.ml2.mech_driver.provisioning_blocks',
            autospec=True)
class TestBindPort(base.NetworkingAnsibleTestCase):
    def test_bind_port_info_no_mac(self,
                                   mock_prov_blks,
                                   mock_vlan_access_port):
        self.mech.bind_port(self.mock_port_context)
        mock_vlan_access_port.assert_called_once()

    def test_bind_port_mac_no_info_local_link_info(self,
                                                   mock_prov_blks,
                                                   mock_vlan_access_port):
        bind_prof = 'binding:profile'
        self.mock_port_context.current[bind_prof] = self.lli_no_info
        self.mech.bind_port(self.mock_port_context)
        mock_vlan_access_port.assert_called_once()

    @mock.patch('networking_ansible.ml2.mech_driver.'
                'AnsibleMechanismDriver._is_port_supported')
    def test_bind_port_port_not_supported(self,
                                          mock_prov_blks,
                                          mock_vlan_access_port,
                                          mock_port_supported):
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


class TestIsPortSupported(base.NetworkingAnsibleTestCase):
    def test_is_port_supported(self):
        self.assertTrue(
            self.mech._is_port_supported(self.mock_port_context.current))

    def test_is_port_supported_not_baremetal(self):
        self.mock_port_context.current['binding:vnic_type'] = 'not-baremetal'
        self.assertFalse(
            self.mech._is_port_supported(self.mock_port_context.current))


@mock.patch('networking_ansible.ml2.mech_driver.'
            'AnsibleMechanismDriver._is_port_supported')
class TestIsPortBound(base.NetworkingAnsibleTestCase):
    def test_is_port_bound(self, mock_port_supported):
        self.assertTrue(
            self.mech._is_port_bound(self.mock_port_context.current))

    def test_is_port_bound_not_other(self, mock_port_supported):
        self.mock_port_context.current['binding:vif_type'] = 'not-other'
        self.assertFalse(
            self.mech._is_port_bound(self.mock_port_context.current))

    def test_is_port_bound_port_not_supported(self, mock_port_supported):
        mock_port_supported.return_value = False
        self.assertFalse(
            self.mech._is_port_bound(self.mock_port_context.current))


@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.create_network')
class TestCreateNetworkPostCommit(base.NetworkingAnsibleTestCase):
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


@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.delete_network')
class TestDeleteNetworkPostCommit(base.NetworkingAnsibleTestCase):
    def test_delete_network_postcommit(self, mock_delete_network):
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_called_once()

    def test_delete_network_postcommit_manage_vlans_false(self,
                                                          mock_delete_network):
        self.inventory['all']['hosts'][self.testhost]['manage_vlans'] = False
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_not_called()

    def test_delete_network_postcommit_fails(self, mock_delete_network):
        mock_delete_network.side_effect = Exception()
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_called_once()

    def test_delete_network_postcommit_not_vlan(self, mock_delete_network):
        self.mock_net_context.current['provider:network_type'] = 'not-vlan'
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_network.assert_not_called()

    def test_delete_network_postcommit_not_segmentation_id(self,
                                                           mock_delete_netwrk):
        self.mock_net_context.current['provider:segmentation_id'] = ''
        self.mech.delete_network_postcommit(self.mock_net_context)
        mock_delete_netwrk.assert_not_called()


@mock.patch('networking_ansible.ml2.mech_driver.'
            'AnsibleMechanismDriver._is_port_bound')
@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.vlan_access_port')
class TestDeletePortPostCommit(base.NetworkingAnsibleTestCase):
    def test_delete_port_postcommit_current(self,
                                            mock_vlan_access,
                                            mock_port_bound):
        self.mech.delete_port_postcommit(self.mock_port_context)
        mock_vlan_access.assert_called_once_with(
            'remove',
            self.mock_port_context.current,
            self.mock_port_context.network.current)

    def test_delete_port_postcommit_not_bound(self,
                                              mock_vlan_access,
                                              mock_port_bound):
        mock_port_bound.return_value = False
        self.mech.delete_port_postcommit(self.mock_port_context)
        mock_vlan_access.assert_not_called()


@mock.patch('networking_ansible.config.build_ansible_inventory', autospec=True)
class TestInit(base.NetworkingAnsibleTestCase):
    def test_intialize(self, mock_inventory):
        self.mech.initialize()
        mock_inventory.assert_called_once_with()


@mock.patch('networking_ansible.ml2.mech_driver.'
            'AnsibleMechanismDriver._is_port_bound')
@mock.patch('networking_ansible.ansible_networking.'
            'AnsibleNetworking.vlan_access_port')
@mock.patch('networking_ansible.ml2.mech_driver.provisioning_blocks',
            autospec=True)
class TestUpdatePortPostCommit(base.NetworkingAnsibleTestCase):
    def test_update_port_postcommit_current(self,
                                            mock_prov_blks,
                                            mock_vlan_access,
                                            mock_port_bound):
        self.mech.update_port_postcommit(self.mock_port_context)
        mock_prov_blks.provisioning_complete.assert_called_once()

    def test_update_port_postcommit_original(self,
                                             mock_prov_blks,
                                             mock_vlan_access,
                                             mock_port_bound):
        mock_port_bound.side_effect = [False, True]
        self.mech.update_port_postcommit(self.mock_port_context)
        mock_vlan_access.assert_called_once()

    def test_update_port_postcommit_not_bound(self,
                                              mock_prov_blks,
                                              mock_vlan_access,
                                              mock_port_bound):
        mock_port_bound.side_effect = [False, False]
        self.mech.update_port_postcommit(self.mock_port_context)
        mock_vlan_access.assert_not_called()
