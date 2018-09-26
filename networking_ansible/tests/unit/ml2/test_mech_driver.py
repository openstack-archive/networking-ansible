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

import contextlib
import mock
import tempfile

import fixtures
from neutron.common import test_lib
from neutron.plugins.ml2.common import exceptions as ml2_exc
from neutron.tests.unit.plugins.ml2 import test_plugin
from neutron_lib.api.definitions import portbindings
from neutron_lib.api.definitions import provider_net
import webob.exc

from networking_ansible import api
from networking_ansible import exceptions
from networking_ansible.ml2 import exceptions as netans_ml2exc
from networking_ansible.tests.unit import base


class TestLibTestConfigFixture(fixtures.Fixture):
    def __init__(self):
        self._original_test_config = None

    def _setUp(self):
        self.addCleanup(self._restore)
        self._original_test_config = test_lib.test_config.copy()

    def _restore(self):
        if self._original_test_config is not None:
            test_lib.test_config = self._original_test_config


class NetAnsibleML2Base(test_plugin.Ml2PluginV2TestCase):
    def setUp(self):
        base.patch_neutron_quotas()
        super(NetAnsibleML2Base, self).setUp()


@mock.patch.object(api.NetworkingAnsible, 'update_access_port')
@mock.patch('networking_ansible.ml2.mech_driver.provisioning_blocks',
            autospec=True)
class TestBindPort(base.NetworkingAnsibleTestCase):
    def test_bind_port(self, mock_prov_blks, mock_update_access_port):
        self.mech.bind_port(self.mock_port_context)
        mock_update_access_port.assert_called_once()

    @mock.patch('networking_ansible.ml2.mech_driver.'
                'AnsibleMechanismDriver._is_port_supported')
    def test_bind_port_port_not_supported(self,
                                          mock_port_supported,
                                          mock_update_access_port,
                                          mock_prov_blks):
        mock_port_supported.return_value = False
        self.mech.bind_port(self.mock_port_context)
        mock_update_access_port.assert_not_called()

    def test_bind_port_no_local_link_info(self,
                                          mock_prov_blks,
                                          mock_update_access_port):
        bind_prof = 'binding:profile'
        local_link_info = 'local_link_information'
        del self.mock_port_context.current[bind_prof][local_link_info]
        self.assertRaises(netans_ml2exc.LocalLinkInfoMissingException,
                          self.mech.bind_port,
                          self.mock_port_context)
        mock_update_access_port.assert_not_called()


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


@mock.patch.object(api.NetworkingAnsible, 'create_vlan')
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


@mock.patch.object(api.NetworkingAnsible, 'delete_vlan')
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
        self.assertRaises(ml2_exc.MechanismDriverError,
                          self.mech.delete_network_postcommit,
                          self.mock_net_context)
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
@mock.patch.object(api.NetworkingAnsible, 'delete_port')
class TestDeletePortPostCommit(base.NetworkingAnsibleTestCase):
    def test_delete_port_postcommit_current(self,
                                            mock_delete_port,
                                            mock_port_bound):
        self.mech.delete_port_postcommit(self.mock_port_context)
        mock_delete_port.assert_called_once_with(self.testhost, self.testport)

    def test_delete_port_postcommit_fails(self,
                                          mock_delete_port,
                                          mock_port_bound):
        mock_delete_port.side_effect = Exception()
        self.assertRaises(ml2_exc.MechanismDriverError,
                          self.mech.delete_port_postcommit,
                          self.mock_port_context)
        mock_delete_port.assert_called_once_with(self.testhost, self.testport)

    def test_delete_port_postcommit_not_bound(self,
                                              mock_delete_port,
                                              mock_port_bound):
        mock_port_bound.return_value = False
        self.mech.delete_port_postcommit(self.mock_port_context)
        mock_delete_port.assert_not_called()


@mock.patch('networking_ansible.config.build_ansible_inventory', autospec=True)
class TestInit(base.NetworkingAnsibleTestCase):
    def test_intialize(self, mock_inventory):
        self.mech.initialize()
        mock_inventory.assert_called_once_with()


@mock.patch('networking_ansible.ml2.mech_driver.'
            'AnsibleMechanismDriver._is_port_bound')
@mock.patch.object(api.NetworkingAnsible, 'delete_port')
@mock.patch('networking_ansible.ml2.mech_driver.provisioning_blocks',
            autospec=True)
class TestUpdatePortPostCommit(base.NetworkingAnsibleTestCase):
    def test_update_port_postcommit_current(self,
                                            mock_prov_blks,
                                            mock_delete_port,
                                            mock_port_bound):
        self.mech.update_port_postcommit(self.mock_port_context)
        mock_prov_blks.provisioning_complete.assert_called_once()

    def test_update_port_postcommit_original(self,
                                             mock_prov_blks,
                                             mock_delete_port,
                                             mock_port_bound):
        mock_port_bound.side_effect = [False, True]
        self.mech.update_port_postcommit(self.mock_port_context)
        mock_delete_port.assert_called_once()

    def test_update_port_postcommit_original_fails(self,
                                                   mock_prov_blks,
                                                   mock_delete_port,
                                                   mock_port_bound):
        mock_port_bound.side_effect = [False, True]
        mock_delete_port.side_effect = Exception()
        self.assertRaises(ml2_exc.MechanismDriverError,
                          self.mech.update_port_postcommit,
                          self.mock_port_context)
        mock_delete_port.assert_called_once()

    def test_update_port_postcommit_not_bound(self,
                                              mock_prov_blks,
                                              mock_delete_port,
                                              mock_port_bound):
        mock_port_bound.side_effect = [False, False]
        self.mech.update_port_postcommit(self.mock_port_context)
        mock_delete_port.assert_not_called()


@mock.patch.object(api.NetworkingAnsible, '_run_task')
class TestML2PluginIntegration(NetAnsibleML2Base):
    _mechanism_drivers = ['ansible']
    HOSTS = ['testinghost', 'otherhost']
    CIDR = '10.0.0.0/24'

    CONFIG_CONTENT = {
        'ansible:{:s}'.format(host): [
            'ansible_network_os=provider\n',
            'ansible_host=host_ip\n',
            'ansible_user=user\n',
            'ansible_pass=password\n',
        ] for host in HOSTS
    }
    CONFIG_CONTENT['ansible:otherhost'].append('manage_vlans=False')

    LOCAL_LINK_INFORMATION = [{
        'switch_info': HOSTS[0],
        'switch_id': 'foo',
        'port_id': 'bar',
    }]

    UNBOUND_PORT_SPEC = {
        'device_owner': 'baremetal:none',
        'device_id': 'some-id',
    }

    BIND_PORT_UPDATE = {
        'port': {
            'binding:host_id': 'foo',
            'binding:vnic_type': portbindings.VNIC_BAREMETAL,
            'binding:profile': {
                'local_link_information': LOCAL_LINK_INFORMATION,
            },
        },
    }

    def setUp(self):
        self.useFixture(TestLibTestConfigFixture())
        self.filename = tempfile.mktemp(prefix='test_anet')
        self._configure()
        super(TestML2PluginIntegration, self).setUp()
        seg_id = self.vlan_range.split(':')[0]
        self.network_spec = {
            provider_net.PHYSICAL_NETWORK: self.physnet,
            provider_net.NETWORK_TYPE: 'vlan',
            provider_net.SEGMENTATION_ID: seg_id,
            'arg_list': (
                provider_net.PHYSICAL_NETWORK,
                provider_net.NETWORK_TYPE,
                provider_net.SEGMENTATION_ID,
            ),
            'admin_state_up': True
        }

    def _write_config_content(self):
        with open(self.filename, 'w') as f:
            for section, content in self.CONFIG_CONTENT.items():
                f.write("[{:s}]\n".format(section))
                f.writelines(content)
                f.write("\n")

    def _configure(self):
        """Create config for the mech driver."""
        test_lib.test_config.setdefault('config_files', []).append(
            self.filename)
        self._write_config_content()

    def _create_network_with_spec(self, name, spec):
        res = self._create_network(self.fmt, name, **spec)
        network = self.deserialize(self.fmt, res)
        return res, network

    def test_create_network_vlan(self, m_run_task):
        res, _ = self._create_network_with_spec('tenant', self.network_spec)
        self.assertEqual(webob.exc.HTTPCreated.code, res.status_int)
        expected_calls = [
            mock.call(
                'create_network',
                host,
                vlan_id=int(self.network_spec[provider_net.SEGMENTATION_ID]))
            for host in self.HOSTS if 'manage_vlans=False' not in
            self.CONFIG_CONTENT['ansible:%s' % host]]
        self.assertItemsEqual(
            expected_calls,
            m_run_task.call_args_list)

    def test_delete_network(self, m_run_task):
        res, network = self._create_network_with_spec('tenant',
                                                      self.network_spec)
        m_run_task.reset_mock()
        req = self.new_delete_request('networks', network['network']['id'])
        res = req.get_response(self.api)
        self.assertEqual(webob.exc.HTTPNoContent.code, res.status_int)
        expected_calls = [
            mock.call(
                'delete_network',
                host,
                vlan_id=int(self.network_spec[provider_net.SEGMENTATION_ID]))
            for host in self.HOSTS if 'manage_vlans=False' not in
            self.CONFIG_CONTENT['ansible:%s' % host]]
        self.assertItemsEqual(
            expected_calls,
            m_run_task.call_args_list)

    @contextlib.contextmanager
    def _create_unbound_port(self):
        """Create a bound port in a network.

        Network is created using self.network_spec defined in the setUp()
        method of this class. Port attributes are defined in the
        UNBOUND_PORT_SPEC.

        """
        with self.network('tenant', **self.network_spec) as n:
            with self.subnet(network=n, cidr=self.CIDR) as s:
                with self.port(
                        subnet=s,
                        **self.UNBOUND_PORT_SPEC
                        ) as p:
                    yield p

    def test_update_port_unbound(self, m_run_task):
        with self._create_unbound_port() as p:
            req = self.new_update_request(
                'ports',
                self.BIND_PORT_UPDATE,
                p['port']['id'])
            m_run_task.reset_mock()

            port = self.deserialize(
                self.fmt, req.get_response(self.api))

            m_run_task.called_once_with(
                'update_port',
                self.HOSTS[0],
                self.LOCAL_LINK_INFORMATION[0]['port_id'],
                self.network_spec[provider_net.SEGMENTATION_ID])
            self.assertNotEqual(
                portbindings.VIF_TYPE_BINDING_FAILED,
                port['port'][portbindings.VIF_TYPE])

    def test_delete_port(self, m_run_task):
        with self._create_unbound_port() as p:
            req = self.new_update_request(
                'ports',
                self.BIND_PORT_UPDATE,
                p['port']['id'])
            port = self.deserialize(
                self.fmt, req.get_response(self.api))
            m_run_task.reset_mock()

            self._delete('ports', port['port']['id'])
            m_run_task.called_once_with(
                'delete_port',
                self.HOSTS[0],
                self.LOCAL_LINK_INFORMATION[0]['port_id'],
                self.network_spec[provider_net.SEGMENTATION_ID])

    def test_update_port_error(self, m_run_task):
        with self._create_unbound_port() as p:
            m_run_task.side_effect = exceptions.AnsibleRunnerException('foo')
            self.assertEqual(
                portbindings.VIF_TYPE_UNBOUND,
                p['port'][portbindings.VIF_TYPE])

            req = self.new_update_request(
                'ports',
                self.BIND_PORT_UPDATE,
                p['port']['id'])
            res = req.get_response(self.api)
            port = self.deserialize(self.fmt, res)
            # NOTE(jlibosva): The port update was successful as the binding was
            # changed. The way how to check the error is via its binding value
            self.assertEqual(
                portbindings.VIF_TYPE_BINDING_FAILED,
                port['port'][portbindings.VIF_TYPE])
            self.assertEqual(webob.exc.HTTPOk.code, res.status_int)
