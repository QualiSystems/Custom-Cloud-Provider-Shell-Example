import random
from data_model import HeavenResidentInstance, Cloud
from typing import List, Dict
from cloudshell.cp.core.models import ConnectSubnet
import uuid


# represents cloud SDK
class HeavenlyCloudService(object):

    @staticmethod
    def get_prefered_cloud_color():
        return 'pink'

    @staticmethod
    def can_connect(user, password, address):
        return True

    @staticmethod
    def allocate_resource():
        pass

    @staticmethod
    def do_other_stuff():
        pass

    @staticmethod
    def power_on(cloud_provider_resource, vm_id):
        pass

    @staticmethod
    def power_off(cloud_provider_resource, vm_id):
        pass

    @staticmethod
    def delete_instance(cloud_provider_resource, vm_id):
        pass

    @staticmethod
    def create_new_password(cloud_provider_resource, user, password):
        return str(uuid.uuid4())

    @staticmethod
    def connect(user, password, address):
        pass

    @staticmethod
    def rollback():
        pass

    @staticmethod
    def create_man_instance(login_user, login_pass, cloud_provider_resource, name, height, weight, cloud_size, image, network_data):
        # connect to cloudprovider
        HeavenlyCloudService.connect(cloud_provider_resource.user, cloud_provider_resource.password,
                                     cloud_provider_resource.address)

        # create the instance and return an object representing the newly created instance
        return HeavenResidentInstance(name, 'height {0} weight {1}'.format(height, weight), image, Cloud(cloud_size),
                                      str(uuid.uuid4()),
                                      '192.168.10.{}'.format(str(random.randint(1, 253))),
                                      '8.8.8.{}'.format(str(random.randint(1, 253))))

    @staticmethod
    def create_angel_instance(login_user, login_pass, cloud_provider_resource, name, wing_count, flight_speed,
                              cloud_size, image, network_data):
        # connect to cloudprovider
        HeavenlyCloudService.connect(cloud_provider_resource.user, cloud_provider_resource.password,
                                     cloud_provider_resource.address)

        # create the instance and return an object representing the newly created instance
        return HeavenResidentInstance(name, 'wing count {0} flight speed {1}'.format(wing_count, flight_speed), image,
                                      Cloud(cloud_size), str(uuid.uuid4()),
                                      '192.168.0.{}'.format(str(random.randint(1, 253))), None)

    @staticmethod
    def get_instance(cloud_provider_resource, name, id, address):
        return HeavenResidentInstance(name, 'instance {0} {1}'.format(name, id), 'centos', Cloud(0), str(id), address,
                                      None)

    @staticmethod
    def set_auth(cloud_provider_resource, user, password):
        pass

    @staticmethod
    def remote_refresh_ip(cloud_provider_resource, cancellation_context, resource_full_name, vm_id):
        HeavenlyCloudService.connect(cloud_provider_resource.user, cloud_provider_resource.password,
                                     cloud_provider_resource.address)

        return '192.168.5.{}'.format(str(random.randint(1, 253)))

    @staticmethod
    def prepare_infra(cloud_provider_resource, cidr):
        pass

    @staticmethod
    def get_or_create_ssh_key():
        return 'sandbox_ssh_key'

    @staticmethod
    def prepare_subnet(subnet_cidr, is_public, attributes):
        return 'subnet_id_{}'.format(str(uuid.uuid4())[:8])


    @staticmethod
    def prepare_network_for_instance(connect_subnet_actions):
        """
        :param List[ConnectSubnet] connect_subnet_actions:
        :return:
        :rtype: Dict
        """
        if not connect_subnet_actions:
            # we are in single subnet mode. need to create the instance in the default subnet
            return {'default_subnet': 0}
        else:
            result = {}
            for index, action in enumerate(connect_subnet_actions):
                # Note:
                # The 'vnicName' prop is the requested vnic to be associated with the given subnet.
                # Here we might want to inspect the vnicName prop to decide how to map subnet ids to instance interfaces.
                # vnic_name = action.actionParams.vnicName
                result[action.actionParams.subnetId] = index

            return result

