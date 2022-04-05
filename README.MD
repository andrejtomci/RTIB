# Red Team Infrastructure Builder (RTIB)
## About
RTIB is a command-line tool focused on red team infrastructure automation. 
It utilizes Terraform modules for configuration orchestration and 
Ansible roles for configuration management.  


For full description of the RTIB's architecture, see the fifth chapter of my [bachelor's thesis](https://is.muni.cz/th/rc4n0/).

## Installation
The prefered way of installing RTIB on a Debian-like system is as follows:
- Install [Terraform](https://learn.hashicorp.com/terraform/getting-started/install.html)
- Install [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- Install Python 3.8   
`$ apt install python3.8`
- Install pip   
`$ apt install python3-pip`
- Install pipenv   
`$ pip3 install pipenv`
- Initialize virtual environment and install dependencies  
`$ python3 -m pipenv install`

## Infrastructure description
RTIB takes a single infrastructure description file as an input, as the example of such file serves [example_infrastructure.yaml](example_infra.yaml).

The desired instances have two important arguments - `provider` and `role`. The former specifies which cloud environment to use (Terraform module), the latter the instance's role in the infrastructure (Ansible role).
Note that both `provider` and `role` values must be present as a directory in `./provider` and `./role` directories respectively.

Every Terraform module and Ansible role has a `README.md` file, containing basic information and available arguments.
**Please, pay attention to those READMEs, especially the ones related to Terraform modules (cloud providers) and provide (update the default) arguments according to your needs.** 

For full description of the RTIB's infrastructure description system, see the fourth chapter of my [bachelor's thesis](https://is.muni.cz/th/rc4n0/).



## Usage
Before running any of the following commands, infrastructure description file must be prepared.
Another important step is to **activate the Pipenv shell**.
To do so, run `python3 -m pipenv shell`.

CLI offers *verbose* mode, which prints the outputs of Terraform and Ansible commands. To turn it on, run the tool with `-v` switch.

build/update the infrastructure:  
`$ python cli.py [infrastructure description file]` 

destroy the infrastructure:  
`$ python cli.py [infrastructure description file] destroy`

run the infrastructure description validation only:  
`$ python cli.py [infrastructure description file] validate`

run the configuration orchestration only:  
`$ python cli.py [infrastructure description file] orchestrate`

run the configuration management only:  
`$ python cli.py [infrastructure description file] manage [inventory file]`

rebuild a single instance in the infrastructure:  
`$ python cli.py [infrastructure description file] rebuild [instance name]`

## Extensibility
You can easily extend the available cloud environments and instance components.

To add a new cloud provider, simply create a new Terraform [module](https://www.terraform.io/docs/configuration/modules.html)
according to your needs and add it to `./providers` folder.
The only requirement is that similarly to other modules, it must provide the public addresses of the build instances in
the module output as `hosts`.

The process of adding a new instance component is even simpler, all you need to do is add your Ansible role to `./roles` directory.

## Tests
To run the enclosed unit tests, execute:   
`$ python -m unittest tests/unit_tests/*.py`

## Troubleshooting
Sometimes, Ansible error occurs because it gets stuck while managing the infrastructure. This is a known [issue](https://serverfault.com/questions/630253/ansible-stuck-on-gathering-facts)
and the quick fix seems to be adding following lines to the `/etc/ansible/ansible.cfg` file:
```
[ssh_connection]
ssh_args = -o ServerAliveInterval=60 -o ControlMaster=auto -o ControlPersist=60s
control_path = none
```

Also try the *verbose* mode, Ansible and Terraform messages are usually very helpful.

In case the problems persist, don't hesitate to contact the [author](#author).

## License
See [LICENSE.txt](LICENSE.txt).

## Author
Andrej Tomči  
Penetration tester @[CSIRT-MU](https://csirt.muni.cz)  
tomci@ics.muni.cz 
