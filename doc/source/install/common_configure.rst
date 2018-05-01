2. Edit the ``/etc/neutron/plugins/ml2/ml2_conf.ini`` file and complete the following
   actions:

   * Create a section for each host with a section name prefixed by ``ansible:``:

     .. code-block:: ini

        [ansible:myhostname]
        ansible_connection=netconf
        ansible_host=10.10.2.250
        ansible_user=ansible
        ansible_ssh_pass=password
