2. Edit the ``/etc/networking_ansible/networking_ansible.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://networking_ansible:NETWORKING_ANSIBLE_DBPASS@controller/networking_ansible
