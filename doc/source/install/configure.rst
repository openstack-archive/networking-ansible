.. _configure:

Configure
~~~~~~~~~

This section decribes how to configure Neutron configuration files to enable
the networking-ansible ML2 driver and configure switch devices that will be
managed by networking-ansible.

#. Configure type_drivers and mechanism_drivers and network_vlan_ranges.

    Add ``vlan`` to ``type_drivers``, ``ansible`` to ``mechanism_drivers``, and
    define the ``network_vlan_range`` that will be used by the openstack networks that use
    this driver.

    .. code-block:: ini

      [ml2]
      type_drivers = vlan
      mechanism_drivers = ansible

      [ml2_type_vlan]
      network_vlan_ranges = physnet1:1000:1099

    * Do not remove other values from these comma delimited lists if there are
      are already values present. Append a comma and your value to the list.
    * physnet1 is an identifier configured in the bridge_mapping
      TODO(radez) doc ref to bridge_mapping
    * the VLAN range (1000:1099 in this example) is provided by the switch
      administor. This range is the VLAN IDs assigned by Neutron when a network is created.


#. Add a section for each switch device that will be managed by networking-ansible.

    Create a section for each host with a section name prefixed by ``ansible:``
    in ``/etc/neutron/plugins/ml2/ml2_conf.ini``.

    .. code-block:: ini

      [ansible:myhostname]
      ansible_network_os=junos
      ansible_host=10.10.2.250
      ansible_user=ansible
      ansible_pass=password

    * myhostname is an arbitrary internal identifier used only in ironic's link_local_information.
    * ansible_network_os is a valid Ansible Networking value to indicate switch type.
      Tested with networking-ansible: openvswitch, junos
      Untested but valid with networking-ansible: eos, nxos
      See contributor/provider for more information.
    * ansible_host is the IP address or hostname used to connect to the switch.
    * ansible_user username of the credentials used to connect to the switch.
    * ansible_pass password of the credentials used to connect to the switch.

    Additional available parameters:

    .. code-block:: ini

      ansible_ssh_private_key_file=/path/to/ansible-ssh
      manage_vlans=True

    * ansible_ssh_private_key_file can be used as an alternative to ansible_pass
      to use ssh key authentication instead of password authentication.
    * manage_vlans is optional and defaults to True. Set this to False for a
      switch if networking-ansible should not create and delete VLANs on the device.


#. Restart the Neutron API service

     .. code-block:: ini

       $ service neturon-server restart
