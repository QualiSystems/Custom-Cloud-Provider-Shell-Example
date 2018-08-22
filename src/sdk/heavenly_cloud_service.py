from data_model import HeavenResidentInstance,Cloud
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
    def power_on(cloud_provider_resource,vm_id):
        pass

    @staticmethod
    def power_off(cloud_provider_resource, vm_id):
        pass

    @staticmethod
    def delete_instance(cloud_provider_resource, vm_id):
        pass

    @staticmethod
    def create_new_password(cloud_provider_resource,user,password):
        return str(uuid.uuid4())

    @staticmethod
    def connect(user, password, address):
        pass

    @staticmethod
    def rollback():
        pass

    @staticmethod
    def create_man_instance(login_user,login_pass, cloud_provider_resource, name, height, weight ,cloud_size, image):
        HeavenlyCloudService.connect(cloud_provider_resource.user, cloud_provider_resource.password, cloud_provider_resource.address)
        return HeavenResidentInstance(name, 'height {0} weight {1}'.format(height, weight ),image, Cloud(cloud_size),str(uuid.uuid4()),'192.168.10.5','8.8.8.8')
        pass

    @staticmethod
    def create_angel_instance(login_user,login_pass, cloud_provider_resource, name, wing_count, flight_speed, cloud_size,image):
        HeavenlyCloudService.connect(cloud_provider_resource.user, cloud_provider_resource.password,
                                      cloud_provider_resource.address)

        return HeavenResidentInstance(name, 'wing count {0} flight speed {1}'.format(wing_count, flight_speed), image,Cloud(cloud_size),str(uuid.uuid4()),'192.168.0.5',None)
        pass

    @staticmethod
    def get_instance(cloud_provider_resource, name ,id,address):
        return HeavenResidentInstance(name, 'instance {0} {1}'.format(name ,id),'centos', Cloud(0),str(id),address,None)

    @staticmethod
    def set_auth(cloud_provider_resource, user, password):
        pass


    @staticmethod
    def remote_refresh_ip(cloud_provider_resource, cancellation_context, resource_full_name, vm_id):
        HeavenlyCloudService.connect(cloud_provider_resource.user, cloud_provider_resource.password,
                                      cloud_provider_resource.address)

        return '5.5.5.1'
