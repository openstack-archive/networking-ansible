Prerequisites
-------------

To successfully install and configure the Networking-Ansible ML2 Driver, you
will need a few prerequisites. Collecting this information and ensuring these
resources are available will ensure a successful installation.

#. Switch credentials that allow configuration changes to the ports that the
   deployed baremetal guests are connected to.

   For security purposes it is important that you do not provide administrator
   access to the switch for networking-ansible. A user should be created
   and granted access for the permissions needed for networking-ansible.

   Networking-Ansible will need to configure a port in access mode and assign
   a VLAN to that port. It will optionally need access to create VLANs if
   you choose not to predefine the VLANs that will be used.

#. OpenStack must be installed with Neutron configured to provide VLAN tenant
   networking.

   This prerequisite is currently outside the scope of this document. Please
   refer to Neutron's documentation or other guides to provide VLAN tenant
   networking.
