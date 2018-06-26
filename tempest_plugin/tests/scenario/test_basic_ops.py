# Copyright 2018 Red Hat, Inc.
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

from tempest.lib import decorators
from tempest.lib import exceptions

from tempest_plugin.tests import base
from tempest_plugin.tests import utils


class TestWithOvs(base.NetAnsibleAdminBaseTest):

    def setUp(self):
        super(TestWithOvs, self).setUp()
        self.ovs = utils.get_idl_singleton()

    def cleanup_port(self, port_id):
        """Remove Neutron port and skip NotFound exceptions."""
        try:
            self.admin_ports_client.delete_port(port_id)
        except exceptions.NotFound:
            pass

    @property
    def ovs_bridge_name(self):
        return 'net-ans-br'

    @property
    def ovs_bridge_mac(self):
        return self.ovs.db_get(
            'Interface', self.ovs_bridge_name, 'mac_in_use').execute()

    def get_network_segmentation_id(self, network_id):
        return self.admin_networks_client.show_network(
            network_id)['network']['provider:segmentation_id']

    def create_port(self, network_id):
        port_name = 'net-ans-p0'
        port = self.admin_ports_client.create_port(
            network_id=network_id, name=port_name)['port']
        self.addCleanup(self.cleanup_port, port['id'])

        host = self.admin_agents_client.list_agents(
            agent_type='Open vSwitch agent'
        )['agents'][0]['host']

        llc = [{'switch_info': 'localhost',
                'switch_id': self.ovs_bridge_mac,
                'port_id': port_name}]

        update_args = {
            'device_owner': 'baremetal:none',
            'device_id': 'fake-instance-uuid',
            'admin_state_up': True,
            'binding:vnic_type': 'baremetal',
            'binding:host_id': host,
            'binding:profile': {
                'local_link_information': llc
            }
        }
        self.admin_ports_client.update_port(
            port['id'],
            **update_args
        )

    @decorators.idempotent_id('40b81fe4-1e9c-4f10-a808-c23f85aea5e2')
    def test_create_port(self):
        net_id = self.admin_networks_client.list_networks(
            name='private')['networks'][0]['id']
        self.create_port(net_id)
        current_tag = self.ovs.db_get('Port', 'net-ans-p0', 'tag').execute()
        network_segmentation_id = self.get_network_segmentation_id(net_id)
        self.assertEqual(network_segmentation_id, current_tag)
