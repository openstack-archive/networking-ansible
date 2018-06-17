#!/bin/bash
# plugin.sh - DevStack plugin.sh dispatch script template

NET_ANSIBLE_DIR=$DEST/networking-ansible
NET_ANSIBLE_ALIAS=ansible
NET_ANSIBLE_CONF=ml2_ansible.conf
NET_ANSIBLE_CONF_FILE=/$Q_PLUGIN_CONF_PATH/$NET_ANSIBLE_CONF

NET_ANSIBLE_OVS_BRIDGE=net-ans-br
NET_ANSIBLE_OVS_PORT=net-ans-p0


function pre_install {
    :
}


function install {
    # Install networking-ansible code to the machine
    echo_summary "Installing networking-ansible bits"
    setup_develop $NET_ANSIBLE_DIR
}


function post_config {
    # The function does following:
    # - adds ansible to the Neutron mech drivers at ML2 plugin configuration file
    # - creates a configuration file for openvswitch bridge and its ports for testing
    # - creates defined bridge and port for testing
    echo_summary "Configuring networking-ansible"

    # Enable the mech driver
    if [[ -z "$Q_ML2_PLUGIN_MECHANISM_DRIVERS" ]]; then
        Q_ML2_PLUGIN_MECHANISM_DRIVERS=$NET_ANSIBLE_ALIAS
    elif [[ ! $Q_ML2_PLUGIN_MECHANISM_DRIVERS =~ "$NET_ANSIBLE_ALIAS" ]]; then
        Q_ML2_PLUGIN_MECHANISM_DRIVERS+=,"$NET_ANSIBLE_ALIAS"
    fi
    populate_ml2_config /$Q_PLUGIN_CONF_FILE ml2 mechanism_drivers=$Q_ML2_PLUGIN_MECHANISM_DRIVERS

    # Create config file for openvswitch ansible module
    populate_ml2_config $NET_ANSIBLE_CONF_FILE openvswitch ip_address 127.0.0.1

    # Create resources for openvswitch
    sudo ovs-vsctl --may-exist add-br $NET_ANSIBLE_OVS_BRIDGE -- --may-exist add-port $NET_ANSIBLE_OVS_BRIDGE $NET_ANSIBLE_OVS_PORT -- set Interface $NET_ANSIBLE_OVS_PORT type=internal
}


function extra {
    echo_summary "Stack extra"
}


function unstack {
    echo_summary "Unstack"
}

function test-config {
    echo_summary "Test config"
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
