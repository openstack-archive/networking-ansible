#!/bin/bash
# plugin.sh - DevStack plugin.sh dispatch script template

NET_ANSIBLE_DIR=$DEST/networking-ansible
NET_ANSIBLE_MECH_DRIVER_ALIAS=ansible
NET_ANSIBLE_ROLES_DIR=$NET_ANSIBLE_DIR/etc/ansible/roles/

ANSIBLE_ROLES_DIR=/etc/ansible/roles

NET_ANSIBLE_OVS_BRIDGE=${NET_ANSIBLE_OVS_BRIDGE:-net-ans-br}
NET_ANSIBLE_OVS_PORT=${NET_ANSIBLE_OVS_PORT:-net-ans-p0}

SSH_KEY_FILE=~/.ssh/id_rsa

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
}


function extra {
    echo_summary "Stack extra"
}


function unstack {
    echo_summary "Unstack"
}

function test-config {
    echo_summary "Test config"

    # Create resources for openvswitch
    sudo ovs-vsctl --may-exist add-br $NET_ANSIBLE_OVS_BRIDGE -- --may-exist add-port $NET_ANSIBLE_OVS_BRIDGE $NET_ANSIBLE_OVS_PORT -- set Interface $NET_ANSIBLE_OVS_PORT type=internal
    sudo ovs-vsctl set Port $NET_ANSIBLE_OVS_PORT tag=[]

    # Allow ansible on localhost
    ssh-keygen -q -t rsa -P '' -f $SSH_KEY_FILE
    cat ${SSH_KEY_FILE}.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
}

function clean {
    echo_summary "Clean"

    sudo ovs-vsctl del-br $NET_ANSIBLE_OVS_BRIDGE
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
