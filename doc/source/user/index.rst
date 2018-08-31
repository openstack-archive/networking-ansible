===========
Users guide
===========

Networking-Ansible is currently tested with one use case, Ironic Baremetal Guests.
In this section this use case will be exercised in a set of example commands to
show how end users would use ironic to provision baremetal nodes. Provisioning
baremetal nodes using ironic with networking-ansible would use networking-ansible
to manage the guest's switch level network configuration. Networking-Ansible is used by
ironic to first assign a baremetal guest's switchport to the Ironic provisoning
network to provision the baremetal guest. After provisoning, the baremetal
guest's switchport is assigned to the VLAN assigned by Neutron to guest's tenant network.

The example shown here mirrors a user's expereience deploying a guest with
Ironic. The end user's experience using networking-ansible is via Neutron and
Nova. Nova will select a baremetal node as its target when a properly configured
baremetal flavor is provided to the OpenStack server create command.

#. An administrator will provide Ironic node(s) that are available for
   provisioning and a baremetal flavor.

  .. code-block:: console

    openstack baremetal node list
    openstack flavor list

#. Create a tenant VLAN network and subnet that uses the physical network the guest is attached to.

  .. code-block:: console

    openstack network create --provider-network-type vlan --provider-physical-network datacentre my-tenant-net
    openstack subnet create --network tenant-net --subnet-range 192.168.3.0/24 --allocation-pool start=192.168.3.10,end=192.168.3.20 tenant-subnet

#. Execute server create using the tenant network just created. This assumes
   disk images and keypairs are already created and available.

  .. code-block:: console

    openstack server create --image a-baremetal-image --flavor baremetal --nic net-id={my-tenant-net uuid} --key-name my-keypair bm-instance
