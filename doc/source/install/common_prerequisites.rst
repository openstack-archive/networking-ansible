Prerequisites
-------------

Before you install and configure the Ansible Networking ML2 Driver service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``networking_ansible`` database:

     .. code-block:: none

        CREATE DATABASE networking_ansible;

   * Grant proper access to the ``networking_ansible`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON networking_ansible.* TO 'networking_ansible'@'localhost' \
          IDENTIFIED BY 'NETWORKING_ANSIBLE_DBPASS';
        GRANT ALL PRIVILEGES ON networking_ansible.* TO 'networking_ansible'@'%' \
          IDENTIFIED BY 'NETWORKING_ANSIBLE_DBPASS';

     Replace ``NETWORKING_ANSIBLE_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``networking_ansible`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt networking_ansible

   * Add the ``admin`` role to the ``networking_ansible`` user:

     .. code-block:: console

        $ openstack role add --project service --user networking_ansible admin

   * Create the networking_ansible service entities:

     .. code-block:: console

        $ openstack service create --name networking_ansible --description "Ansible Networking ML2 Driver" ansible networking ml2 driver

#. Create the Ansible Networking ML2 Driver service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        ansible networking ml2 driver public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        ansible networking ml2 driver internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        ansible networking ml2 driver admin http://controller:XXXX/vY/%\(tenant_id\)s
