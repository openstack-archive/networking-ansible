#!/bin/bash
# plugin.sh - DevStack plugin.sh dispatch script template

NET_ANSIBLE_DIR=$DEST/networking-ansible
NET_ANSIBLE_MECH_DRIVER_ALIAS=ansible
NET_ANSIBLE_ROLES_DIR=$NET_ANSIBLE_DIR/etc/ansible/roles/

ANSIBLE_ROLES_DIR=/etc/ansible/roles

NET_ANS_SWITCH_INI_FILE="/etc/neutron/plugins/ml2/ml2_conf_netansible.ini"
OVS_SWITCH_DATA_DIR="$DATA_DIR/ovs-switch"
# NOTE(pas-ha) NEVER SET THIS TO ANY EXISTING USER!
# you might get locked out of SSH when limitinig SSH sessions is enabled for this user,
# AND THIS USER WILL BE DELETED TOGETHER WITH ITS HOME DIR ON UNSTACK/CLEANUP!!!
# this is why it is left unconfigurable
OVS_SWITCH_USER="ovs_manager"
OVS_SWITCH_USER_HOME="$OVS_SWITCH_DATA_DIR/$OVS_SWITCH_USER"
OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE="$OVS_SWITCH_USER_HOME/.ssh/authorized_keys"
OVS_SWITCH_KEY_FILE=${OVS_SWITCH_KEY_FILE:-"$OVS_SWITCH_DATA_DIR/keys/ovs-switch"}

OVS_SWITCH_TEST_BRIDGE="ovsswitch"
OVS_SWITCH_TEST_PORT="sw-port-01"


function ansible_workarounds {
    sudo pip uninstall ansible -y

    # This is a workaround for issue https://github.com/ansible/ansible/issues/42108
    # fix is currenlty merged in devel branch, requested as a backport to 2.6
    # until we have a build with the fix, we compile upstream devel branch
    pushd /opt/stack
    git clone https://github.com/ansible/ansible.git
    cd ansible
    git checkout stable-2.6
    python setup.py build
    sudo python setup.py install
    popd
}

function create_ovs_manager_user {
    # Give the non-root user the ability to run as **root** via ``sudo``
    is_package_installed sudo || install_package sudo

    if ! getent group $OVS_SWITCH_USER >/dev/null; then
        echo "Creating a group called $OVS_SWITCH_USER"
        sudo groupadd $OVS_SWITCH_USER
    fi

    if ! getent passwd $OVS_SWITCH_USER >/dev/null; then
        echo "Creating a user called $OVS_SWITCH_USER"
        mkdir -p $OVS_SWITCH_USER_HOME
        sudo useradd -g $OVS_SWITCH_USER -s /bin/bash -d $OVS_SWITCH_USER_HOME -m $OVS_SWITCH_USER
    fi

    echo "Giving $OVS_SWITCH_USER user passwordless sudo privileges"
    # UEC images ``/etc/sudoers`` does not have a ``#includedir``, add one
    sudo grep -q "^#includedir.*/etc/sudoers.d" /etc/sudoers ||
        echo "#includedir /etc/sudoers.d" | sudo tee -a /etc/sudoers
    ( umask 226 && echo "$OVS_SWITCH_USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/99_ovs_manager )

}

function configure_switch_ssh_keypair {
    if [[ ! -d $OVS_SWITCH_USER_HOME/.ssh ]]; then
        sudo mkdir -p $OVS_SWITCH_USER_HOME/.ssh
        sudo chmod 700 $OVS_SWITCH_USER_HOME/.ssh
    fi
    # copy over stack user's authorized_keys to OVS_SWITCH_USER
    # mostly needed for multinode gate job
    if [[ -e "$HOME/.ssh/authorized_keys" ]];then
        cat "$HOME/.ssh/authorized_keys" | sudo tee -a $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
    fi
    if [[ ! -e $OVS_SWITCH_KEY_FILE ]]; then
        if [[ ! -d $(dirname $OVS_SWITCH_KEY_FILE) ]]; then
            mkdir -p $(dirname $OVS_SWITCH_KEY_FILE)
        fi
        ssh-keygen -q -t rsa -P '' -f $OVS_SWITCH_KEY_FILE
    fi
    # NOTE(vsaienko) check for new line character, add if doesn't exist.
    if [[ "$(sudo tail -c1 $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE | wc -l)" == "0" ]]; then
        echo "" | sudo tee -a $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
    fi
    cat $OVS_SWITCH_KEY_FILE.pub | sudo tee -a $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
    # remove duplicate keys.
    sudo sort -u -o $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
    sudo chown $OVS_SWITCH_USER:$OVS_SWITCH_USER $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
    sudo chown -R $OVS_SWITCH_USER:$OVS_SWITCH_USER $OVS_SWITCH_USER_HOME
}

function pre_install {
    # REVISIT(jlibosva): Ubuntu boxes use mawk by default which has a slightly
    #                    different syntax than gawk.  mawk fails when merging
    #                    local.conf with openstack config files.  gawk is a
    #                    requirement of nova and when devstack is used without
    #                    nova, gawk is not installed and the whole devstack
    #                    deployment fails.  The real fix should go to devstack
    #                    repository but until it's fixed there, we have this
    #                    workarond to unblock the CI.
    install_package gawk
}


function install_ansible_roles {
    #TODO: Do this via setuptools
    sudo mkdir -p $ANSIBLE_ROLES_DIR
    sudo cp -r $NET_ANSIBLE_ROLES_DIR/* $ANSIBLE_ROLES_DIR/.
}


function install {
    # Install networking-ansible code to the machine
    echo_summary "Installing networking-ansible bits and its dependencies"
    install_package ansible
    setup_develop $NET_ANSIBLE_DIR
    install_ansible_roles
}

function add_ovs_switch_to_ml2_config {
    local switch_name=$1
    local key_file=$2
    local username=$3
    local ip=$4
    local switch_mac=$5

    populate_ml2_config $NET_ANS_SWITCH_INI_FILE $switch_name ansible_network_os=openvswitch
    populate_ml2_config $NET_ANS_SWITCH_INI_FILE $switch_name ansible_user=$username
    populate_ml2_config $NET_ANS_SWITCH_INI_FILE $switch_name ansible_ssh_private_key_file=$key_file
    populate_ml2_config $NET_ANS_SWITCH_INI_FILE $switch_name ansible_host=$ip
    populate_ml2_config $NET_ANS_SWITCH_INI_FILE $switch_name manage_vlans=False
    if [[ "$switch_mac" != "" ]]; then
        populate_ml2_config $NET_ANS_SWITCH_INI_FILE $switch_name mac=$switch_mac
    fi
}

function post_config {
    # The function does following:
    # - adds ansible to the Neutron mech drivers at ML2 plugin configuration file
    # - creates a configuration file for openvswitch bridge and its ports for testing
    # - creates defined bridge and port for testing
    echo_summary "Configuring networking-ansible"

    # Enable the mech driver
    if [[ -z "$Q_ML2_PLUGIN_MECHANISM_DRIVERS" ]]; then
        Q_ML2_PLUGIN_MECHANISM_DRIVERS=$NET_ANSIBLE_MECH_DRIVER_ALIAS
    elif [[ ! $Q_ML2_PLUGIN_MECHANISM_DRIVERS =~ "$NET_ANSIBLE_MECH_DRIVER_ALIAS" ]]; then
        Q_ML2_PLUGIN_MECHANISM_DRIVERS+=,"$NET_ANSIBLE_MECH_DRIVER_ALIAS"
    fi
    populate_ml2_config /$Q_PLUGIN_CONF_FILE ml2 mechanism_drivers=$Q_ML2_PLUGIN_MECHANISM_DRIVERS

    ansible_workarounds

    create_ovs_manager_user
    configure_switch_ssh_keypair

    sudo ovs-vsctl --may-exist add-br $OVS_SWITCH_TEST_BRIDGE
    sudo ovs-vsctl --may-exist add-port $OVS_SWITCH_TEST_BRIDGE $OVS_SWITCH_TEST_PORT -- set Interface $OVS_SWITCH_TEST_PORT type=internal

    # Create generic_switch ml2 config
    for switch in $OVS_SWITCH_TEST_BRIDGE $IRONIC_VM_NETWORK_BRIDGE; do
        local bridge_mac
        bridge_mac=$(ip link show dev $switch | awk '/ether [A-Za-z0-9:]+/{ print $2 }')
        switch="ansible:$switch"
        add_ovs_switch_to_ml2_config $switch $OVS_SWITCH_KEY_FILE $OVS_SWITCH_USER localhost $bridge_mac
    done
    echo "HOST_TOPOLOGY: $HOST_TOPOLOGY"
    echo "HOST_TOPOLOGY_SUBNODES: $HOST_TOPOLOGY_SUBNODES"
    if [ -n "$HOST_TOPOLOGY_SUBNODES" ]; then
        # NOTE(vsaienko) with multinode topology we need to add switches from all
        # the subnodes to the config on primary node
        local cnt=0
        local section
        for node in $HOST_TOPOLOGY_SUBNODES; do
            cnt=$((cnt+1))
            section="ansible:sub${cnt}${IRONIC_VM_NETWORK_BRIDGE}"
            add_ovs_switch_to_ml2_config $section $OVS_SWITCH_KEY_FILE $OVS_SWITCH_USER $node
        done
    fi

    neutron_server_config_add $NET_ANS_SWITCH_INI_FILE
}


function extra {
    echo_summary "Stack extra"
}


function unstack {
    echo_summary "Unstack"

    rm -f $NET_ANS_SWITCH_INI_FILE
    if [[ -f $OVS_SWITCH_KEY_FILE ]]; then
        local key
        key=$(cat $OVS_SWITCH_KEY_FILE.pub)
        # remove public key from authorized_keys
        sudo grep -v "$key" $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE > temp && sudo mv -f temp $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
        sudo chown $OVS_SWITCH_USER:$OVS_SWITCH_USER $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
        sudo chmod 0600 $OVS_SWITCH_KEY_AUTHORIZED_KEYS_FILE
    fi
    sudo ovs-vsctl --if-exists del-br $OVS_SWITCH_TEST_BRIDGE

    # remove generic switch user, its permissions and limits
    sudo rm -f /etc/sudoers.d/99_ovs_manager
    sudo userdel --remove --force $OVS_SWITCH_USER
    sudo groupdel $OVS_SWITCH_USER

    sudo rm -rf $OVS_SWITCH_DATA_DIR
}

function test-config {
    echo_summary "Test config"
}

function clean {
    echo_summary "Clean"
}


# Devstack plugin skeleton

# check for service enabled
if is_service_enabled networking_ansible; then
    case "$1" in
        stack)
            case "$2" in
                pre-install)
                    pre_install
                    ;;
                post-config)
                    post_config
                    ;;
                *)
                    $2
                    ;;
            esac
            ;;

        *)
            $1
            ;;
    esac
fi
