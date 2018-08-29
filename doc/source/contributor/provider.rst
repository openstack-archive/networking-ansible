================
Provider Support
================
Networking-Ansible contains provider switch specific functionality in an
Ansible role that enables specific hardware devices per provider switch added
to this role. The openstack-ml2 Ansible role is stored in networking-ansible's
etc/ansible/roles directory. A provider switch will be refered to as just a
provider for the remainder of this document.

Adding a provider
~~~~~~~~~~~~~~~~~
To add a provider to networking-ansible's capabilities the provider must be
added to the Ansible openstack-ml2 role. To add the provider to the
openstack-ml2 role a new directory using the Ansible Networking module name
[`1`_] must be added that contains files that will define the Ansible tasks
nessessary to perform the respective ML2 action.

Inside the directory for the provider, a file for default values, plus a file
for each supported action in netwoking-ansible is required. There are currently
five files required to add full functionality for a provider in
networking-ansible.

* defaults.yaml

  Defines default values for segmentation name and ID. For example some
  switch vendors use the name "default" and VLAN ID 1 as a default VLAN
  to assign switchports to. Open vSwitch expects no VLAN ID and VLAN name
  in the case that port is not assigned to a specific VLAN.

* create_network.yaml

  Defines the Ansible tasks to create a VLAN on a switch.

* delete_network.yaml

  Defines the Ansible tasks to delete a VLAN on a switch.

* update_port.yaml

  Defines the Ansible tasks to assign a VLAN to a switchport in access mode.

* delete_port.yaml

  Defines the Ansible tasks to remove configuration from a switchport.

[1] https://docs.ansible.com/ansible/2.5/modules/list_of_network_modules.html

.. _1: https://docs.ansible.com/ansible/2.5/modules/list_of_network_modules.html
