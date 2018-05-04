2. Edit the ``/etc/neutron/plugins/ml2/ml2_conf.ini`` file and complete the following
   actions:

   * Create a section for each host with a section name prefixed by ``ansible:``:

     .. code-block:: ini

        [ansible:myhostname]
        ansible_network_os=vyos
        ansible_host=10.10.2.250
        ansible_user=ansible
        ansible_pass=password

   * myhostname is an internal identifier used in ironic's link_local_information
   * ansible_network_os is a valid Ansible Networking value to indicate switch type
   * ansible_host is the IP address or hostname used to connect to the switch
   * ansible user and pass are credentials used to connect to the switch 
