bind-api
===============

Bind REST API server
Based on the work of https://github.com/aravindavk/glusterfs-rest.git

## Installation

    git clone https://github.com/elianmarks/bind_api.git
    cd bind_api
    sudo python setup.py install
    sudo bindrest install # (Reinstall also available, sudo bindrest reinstall)

## Usage

Start the bindrest service using `sudo bindrestd`

`sudo bindrest --help` for more details.

## CLI Guide

**Available Groups and Permissions**

    binduser  - dnsinfo
    bindadmin - dnsinfo, dnscreate
    bindroot  - dnsinfo, dnscreate, dnsdelete, dnsreplace

**Create a REST user**  

    sudo bindrest useradd <USERNAME> -g <GROUPNAME>

**Delete a REST user**  

    sudo bindrest userdel <USERNAME>

**Modify user Group**  

    sudo bindrest usermod <USERNAME> -g <GROUPNAME>

**To change the user password**  

    sudo bindrest passwd <USERNAME>

**Modify REST server PORT**  

By default it runs in port 9000, to change

    sudo bindrest port 80

**View Information about REST users, config or Groups**  

    sudo bindrest show users
    sudo bindrest show config
    sudo bindrest show groups

## API documentation

Quick summary of APIs available, for detailed documentation run `sudo bindrestd` and visit [https://dns-api.tjmt.jus.br/doc](https://dns-api.tjmt.jus.br/doc)

    Get a DNS Info          POST     /dnsinfo
    Create a DNS            POST    /dnscreate
    Delete a DNS            POST    /dnsdelete
    Replace a DNS           GET    /reversereload
