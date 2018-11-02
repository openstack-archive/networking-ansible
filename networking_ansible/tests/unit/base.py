# Copyright (c) 2018 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
from neutron.plugins.ml2 import driver_context
from neutron.tests.unit.plugins.ml2 import test_plugin

from networking_ansible import config
from networking_ansible.ml2 import mech_driver

QUOTA_REGISTRIES = (
    "neutron.quota.resource_registry.unregister_all_resources",
    "neutron.quota.resource_registry.register_resource_by_name",
)


class NetworkingAnsibleTestCase(test_plugin.Ml2PluginV2TestCase):
    def setUp(self):
        # This is to avoid "No resource found" messages printed to stderr from
        # quotas Neutron code.
        for func in QUOTA_REGISTRIES:
            mock.patch(func).start()
        super(NetworkingAnsibleTestCase, self).setUp()
        self.ansconfig = config
        self.testmac = '01:23:45:67:89:ab'
        self.testhost = 'testhost'
        self.inventory = {
            'all': {
                'hosts': {
                    self.testhost: {
                        'mac': self.testmac
                    }
                }
            }
        }

        with mock.patch('networking_ansible.ml2.mech_driver.config') as m_cfg:
            m_cfg.build_ansible_inventory.return_value = self.inventory
            self.mech = mech_driver.AnsibleMechanismDriver()
            self.mech.initialize()
        self.testsegid = '37'
        self.testport = 'switchportid'
        self.empty_inventory = {'all': {'hosts': {}}}

        # Define mocked network context
        self.mock_net_context = mock.create_autospec(
            driver_context.NetworkContext).return_value
        self.mock_net_context.current = {
            'id': 37,
            'provider:network_type': 'vlan',
            'provider:segmentation_id': self.testsegid,
            'provider:physical_network': 'physnet'}

        # define mocked port context
        self.mock_port_context = mock.create_autospec(
            driver_context.PortContext).return_value
        self.lli_no_mac = {
            'local_link_information': [{
                'switch_info': self.testhost,
                'port_id': self.testport,
            }]
        }
        self.lli_no_info = {
            'local_link_information': [{
                'switch_id': self.testmac,
                'port_id': self.testport,
            }]
        }
        self.mock_port_context.current = {
            'id': 'aaaa-bbbb-cccc',
            'binding:profile': self.lli_no_mac,
            'binding:vnic_type': 'baremetal',
            'binding:vif_type': 'other',
        }
        self.mock_port_context._plugin_context = mock.MagicMock()
        self.mock_port_context.network = mock.Mock()
        self.mock_port_context.network.current = {
            'id': 'aaaa-bbbb-cccc',
            # TODO(radez) should an int be use here or str ok?
            'provider:segmentation_id': self.testsegid,
        }
        self.mock_port_context.segments_to_bind = [
            self.mock_port_context.network.current
        ]
