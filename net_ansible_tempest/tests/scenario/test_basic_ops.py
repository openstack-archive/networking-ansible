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

from oslo_config import cfg
from tempest.lib import decorators
from tempest.lib import exceptions

from net_ansible_tempest.tests import base
from net_ansible_tempest.tests import utils


class TestWithOvs(base.NetAnsibleAdminBaseTest):

    @classmethod
    def skip_checks(cls):
        super(TestWithOvs, cls).skip_checks()
        if not cfg.CONF.service_available.netansible:
            raise cls.skipException("networking ansible is not enabled")

    def setUp(self):
        super(TestWithOvs, self).setUp()
        self.ovs = utils.get_idl_singleton()
        self.network = self.create_network()

    def cleanup_port(self, port_id):
        """Remove Neutron port and skip NotFound exceptions."""
        try:
            self.admin_ports_client.delete_port(port_id)
        except exceptions.NotFound:
            pass

    @property
    def ovs_bridge_name(self):
        return cfg.CONF.net_ansible_openvswitch.bridge_name

    @property
    def ovs_bridge_mac(self):
        return self.ovs.db_get(
            'Interface', self.ovs_bridge_name, 'mac_in_use').execute()

    @property
    def switch_name(self):
        return cfg.CONF.net_ansible_openvswitch.switch_name

    @property
    def ovs_port_name(self):
        return cfg.CONF.net_ansible_openvswitch.port_name

    def get_network_segmentation_id(self, network_id):
        return self.admin_networks_client.show_network(
            network_id)['network']['provider:segmentation_id']

    def create_port(self, network_id, local_link_info):
        port = self.admin_ports_client.create_port(
            network_id=network_id, name=self.ovs_port_name)['port']
        self.addCleanup(self.cleanup_port, port['id'])

        host = self.admin_agents_client.list_agents(
            agent_type='Open vSwitch agent'
        )['agents'][0]['host']

        update_args = {
            'device_owner': 'baremetal:none',
            'device_id': 'fake-instance-uuid',
            'admin_state_up': True,
            'binding:vnic_type': 'baremetal',
            'binding:host_id': host,
            'binding:profile': {
                'local_link_information': local_link_info
            }
        }
        self.admin_ports_client.update_port(
            port['id'],
            **update_args
        )
        return port

    def _test_update_port(self, local_link_info):
        port = self.create_port(self.network['id'], local_link_info)
        current_tag = self.ovs.db_get(
            'Port', self.ovs_port_name, 'tag').execute()
        network_segmentation_id = self.get_network_segmentation_id(
            self.network['id'])
        self.assertEqual(network_segmentation_id, current_tag)

        self.cleanup_port(port['id'])
        current_tag = self.ovs.db_get(
            'Port', self.ovs_port_name, 'tag').execute()
        self.assertEqual([], current_tag)

    @decorators.idempotent_id('40b81fe4-1e9c-4f10-a808-c23f85aea5e2')
    def test_update_port(self):
        local_link_info = [{'switch_info': self.switch_name,
                            'port_id': self.ovs_port_name}]
        self._test_update_port(local_link_info)

    @decorators.idempotent_id('40b81fe4-1e9c-4f10-a808-c23f85aea5e3')
    def test_update_port_no_info(self):
        local_link_info = [{'switch_id': '01:23:45:67:89:ab',
                            'port_id': self.ovs_port_name}]
        self._test_update_port(local_link_info)
