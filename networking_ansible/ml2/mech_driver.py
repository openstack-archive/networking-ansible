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

from neutron.db import provisioning_blocks
from neutron.plugins.ml2.common import exceptions as ml2_exc
from neutron_lib.api.definitions import portbindings
from neutron_lib.callbacks import resources
from neutron_lib.plugins.ml2 import api
from oslo_log import log as logging

from networking_ansible import ansible_networking
from networking_ansible import config

LOG = logging.getLogger(__name__)

ANSIBLE_NETWORKING_ENTITY = 'ANSIBLENETWORKING'


class AnsibleMechanismDriver(api.MechanismDriver):
    """ML2 Mechanism Driver for Ansible Networking

    https://www.ansible.com/integrations/networks
    """

    def initialize(self):
        LOG.debug("Initializing Ansible ML2 driver")

        inventory = config.build_ansible_inventory()
        self.ansnet = ansible_networking.AnsibleNetworking(inventory)

    def create_network_postcommit(self, context):
        """Create a network.

        :param context: NetworkContext instance describing the new
        network.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.
        """

        network = context.current
        network_id = network['id']
        provider_type = network['provider:network_type']
        segmentation_id = network['provider:segmentation_id']
        # physnet = network['provider:physical_network']

        if provider_type == 'vlan' and segmentation_id:
            # assuming all hosts
            # TODO(radez): can we filter by physnets?
            for host_name in self.ansnet.inventory['all']['hosts']:
                host = self.ansnet.inventory['all']['hosts'][host_name]
                if host.get('manage_vlans', True):
                    # Create VLAN on the switch
                    try:
                        self.ansnet.create_network(host_name, segmentation_id)
                        LOG.info('Network {net_id} has been added on ansible '
                                 'host {host}'.format(
                                     net_id=network['id'],
                                     host=host_name))

                    except Exception as e:
                        # TODO(radez) I don't think there is a message returned
                        #             from ansible runner's exceptions
                        LOG.error('Failed to create network {net_id} '
                                  'on ansible host: {host}, '
                                  'reason: {err}'.format(
                                      net_id=network_id,
                                      host=host_name,
                                      err=e))
                        raise ml2_exc.MechanismDriverError(e)

    def delete_network_postcommit(self, context):
        """Delete a network.

        :param context: NetworkContext instance describing the current
        state of the network, prior to the call to delete it.

        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """

        network = context.current
        provider_type = network['provider:network_type']
        segmentation_id = network['provider:segmentation_id']
        # physnet = network['provider:physical_network']

        if provider_type == 'vlan' and segmentation_id:
            # assuming all hosts
            # TODO(radez): can we filter by physnets?
            for host_name in self.ansnet.inventory['all']['hosts']:
                host = self.ansnet.inventory['all']['hosts'][host_name]
                if host.get('manage_vlans', True):
                    # Delete VLAN on the switch
                    try:
                        self.ansnet.delete_network(host_name, segmentation_id)
                        LOG.info('Network {net_id} has been deleted on '
                                 'ansible host {host}'.format(
                                     net_id=network['id'],
                                     host=host_name))

                    except Exception as e:
                        LOG.error('Failed to delete network {net_id} '
                                  'on ansible host: {host}, '
                                  'reason: {err}'.format(net_id=network['id'],
                                                         host=host_name,
                                                         err=e))

    def update_port_postcommit(self, context):
        """Update a port.

        :param context: PortContext instance describing the new
        state of the port, as well as the original state prior
        to the update_port call.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Raising an exception will
        result in the deletion of the resource.
        update_port_postcommit is called for all changes to the port
        state. It is up to the mechanism driver to ignore state or
        state changes that it does not know or care about.
        """
        port = context.network.current
        if self._is_port_bound(context.current):
            provisioning_blocks.provisioning_complete(
                context._plugin_context, port['id'], resources.PORT,
                ANSIBLE_NETWORKING_ENTITY)
        elif self._is_port_bound(context.original):
            # The port has been unbound. This will cause the local link
            # information to be lost, so remove the port from the network on
            # the switch now while we have the required information.
            self.ansnet.vlan_access_port('remove', context.original, port)

    def delete_port_postcommit(self, context):
        """Delete a port.

        :param context: PortContext instance describing the current
        state of the port, prior to the call to delete it.

        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        if self._is_port_bound(context.current):
            self.ansnet.vlan_access_port('remove',
                                         context.current,
                                         context.network.current)

    def bind_port(self, context):
        """Attempt to bind a port.

        :param context: PortContext instance describing the port

        This method is called outside any transaction to attempt to
        establish a port binding using this mechanism driver. Bindings
        may be created at each of multiple levels of a hierarchical
        network, and are established from the top level downward. At
        each level, the mechanism driver determines whether it can
        bind to any of the network segments in the
        context.segments_to_bind property, based on the value of the
        context.host property, any relevant port or network
        attributes, and its own knowledge of the network topology. At
        the top level, context.segments_to_bind contains the static
        segments of the port's network. At each lower level of
        binding, it contains static or dynamic segments supplied by
        the driver that bound at the level above. If the driver is
        able to complete the binding of the port to any segment in
        context.segments_to_bind, it must call context.set_binding
        with the binding details. If it can partially bind the port,
        it must call context.continue_binding with the network
        segments to be used to bind at the next lower level.

        If the binding results are committed after bind_port returns,
        they will be seen by all mechanism drivers as
        update_port_precommit and update_port_postcommit calls. But if
        some other thread or process concurrently binds or updates the
        port, these binding results will not be committed, and
        update_port_precommit and update_port_postcommit will not be
        called on the mechanism drivers with these results. Because
        binding results can be discarded rather than committed,
        drivers should avoid making persistent state changes in
        bind_port, or else must ensure that such state changes are
        eventually cleaned up.

        Implementing this method explicitly declares the mechanism
        driver as having the intention to bind ports. This is inspected
        by the QoS service to identify the available QoS rules you
        can use with ports.
        """
        port = context.current
        binding_profile = port['binding:profile']
        local_link_info = binding_profile.get('local_link_information')
        # Validate port and local link info
        if not (self._is_port_supported(port) and local_link_info):
            # TODO(radez) log debug messages here
            return

        switch_mac = local_link_info[0].get('switch_id', '').upper()
        switch_name = local_link_info[0].get('switch_info')
        switch_port = local_link_info[0].get('port_id')
        # fill in the switch name if mac exists but name is not defined
        # this provides support for introspection when the switch's mac is
        # also provided in the ML2 conf for ansible-networking
        if not switch_name and switch_mac in self.ansnet.mac_map:
            switch_name = self.ansnet.mac_map[switch_mac]

        network = context.network.current
        # If segmentation ID is None, vlan will be set to 1
        segmentation_id = network['provider:segmentation_id'] or '1'
        segments = context.segments_to_bind

        provisioning_blocks.add_provisioning_component(
            context._plugin_context, port['id'], resources.PORT,
            ANSIBLE_NETWORKING_ENTITY)
        LOG.debug("Putting port {port} on {switch_name} to vlan: "
                  "{segmentation_id}".format(
                      port=switch_port,
                      switch_name=switch_name,
                      segmentation_id=segmentation_id))
        # Assign port to network
        self.ansnet.vlan_access_port('assign', context.current,
                                     context.network.current)
        LOG.info("Successfully bound port {port_id} in segment "
                 "{segment_id} on host {host}".format(
                     port_id=port['id'],
                     host=switch_name,
                     segment_id=segmentation_id))
        context.set_binding(segments[0][api.ID],
                            portbindings.VIF_TYPE_OTHER, {})

    @staticmethod
    def _is_port_supported(port):
        """Return whether a port is supported by this driver.

        :param port: The port to check
        :returns: Whether the port is supported

        Ports supported by this driver have a VNIC type of 'baremetal'.
        """
        vnic_type = port[portbindings.VNIC_TYPE]
        return vnic_type == portbindings.VNIC_BAREMETAL

    @staticmethod
    def _is_port_bound(port):
        """Return whether a port is bound by this driver.

        Ports bound by this driver have their VIF type set to 'other'.

        :param port: The port to check
        :returns: Whether the port is bound
        """
        if not AnsibleMechanismDriver._is_port_supported(port):
            return False

        vif_type = port[portbindings.VIF_TYPE]
        return vif_type == portbindings.VIF_TYPE_OTHER
