from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadDetails, AutoLoadAttribute, \
    AutoLoadResource
from collections import defaultdict
from cloudshell.cp.core.utils import *

class LegacyUtils(object):
    def __init__(self):
        self._datamodel_clss_dict = self.__generate_datamodel_classes_dict()

    def migrate_autoload_details(self, autoload_details, context):
        model_name = context.resource.model
        root_name = context.resource.name
        root = self.__create_resource_from_datamodel(model_name, root_name)
        attributes = self.__create_attributes_dict(autoload_details.attributes)
        self.__attach_attributes_to_resource(attributes, '', root)
        self.__build_sub_resoruces_hierarchy(root, autoload_details.resources, attributes)
        return root

    def __create_resource_from_datamodel(self, model_name, res_name):
        return self._datamodel_clss_dict[model_name](res_name)

    def __create_attributes_dict(self, attributes_lst):
        d = defaultdict(list)
        for attribute in attributes_lst:
            d[attribute.relative_address].append(attribute)
        return d

    def __build_sub_resoruces_hierarchy(self, root, sub_resources, attributes):
        d = defaultdict(list)
        for resource in sub_resources:
            splitted = resource.relative_address.split('/')
            parent = '' if len(splitted) == 1 else resource.relative_address.rsplit('/', 1)[0]
            rank = len(splitted)
            d[rank].append((parent, resource))

        self.__set_models_hierarchy_recursively(d, 1, root, '', attributes)

    def __set_models_hierarchy_recursively(self, dict, rank, manipulated_resource, resource_relative_addr, attributes):
        if rank not in dict: # validate if key exists
            pass

        for (parent, resource) in dict[rank]:
            if parent == resource_relative_addr:
                sub_resource = self.__create_resource_from_datamodel(
                    resource.model.replace(' ', ''),
                    resource.name)
                self.__attach_attributes_to_resource(attributes, resource.relative_address, sub_resource)
                manipulated_resource.add_sub_resource(
                    self.__slice_parent_from_relative_path(parent, resource.relative_address), sub_resource)
                self.__set_models_hierarchy_recursively(
                    dict,
                    rank + 1,
                    sub_resource,
                    resource.relative_address,
                    attributes)

    def __attach_attributes_to_resource(self, attributes, curr_relative_addr, resource):
        for attribute in attributes[curr_relative_addr]:
            setattr(resource, attribute.attribute_name.lower().replace(' ', '_'), attribute.attribute_value)
        del attributes[curr_relative_addr]

    def __slice_parent_from_relative_path(self, parent, relative_addr):
        if parent is '':
            return relative_addr
        return relative_addr[len(parent) + 1:] # + 1 because we want to remove the seperator also

    def __generate_datamodel_classes_dict(self):
        return dict(self.__collect_generated_classes())

    def __collect_generated_classes(self):
        import sys, inspect
        return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class HeavenlyCloudShell(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'HeavenlyCloudShell'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype HeavenlyCloudShell
        """
        result = HeavenlyCloudShell(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'HeavenlyCloudShell'

    @property
    def user(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.User'] if 'HeavenlyCloudShell.User' in self.attributes else None

    @user.setter
    def user(self, value):
        """
        user name
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.User'] = value

    @property
    def password(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.Password'] if 'HeavenlyCloudShell.Password' in self.attributes else None

    @password.setter
    def password(self, value):
        """
        password
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.Password'] = value

    @property
    def heaven_cloud_color(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.Heaven cloud color'] if 'HeavenlyCloudShell.Heaven cloud color' in self.attributes else None

    @heaven_cloud_color.setter
    def heaven_cloud_color(self, value):
        """
        color of a cloud
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.Heaven cloud color'] = value
    @property
    def address(self):
        """
        :rtype: str
        """
        return self.attributes[
            'HeavenlyCloudShell.address'] if 'HeavenlyCloudShell.address' in self.attributes else None

    @address.setter
    def address(self, value):
        """
        address
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.address'] = value
    @property
    def default_storage(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.Default storage'] if 'HeavenlyCloudShell.Default storage' in self.attributes else None

    @default_storage.setter
    def default_storage(self, value):
        """
        default storage
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.Default storage'] = value

    @property
    def networking_type(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.Networking type'] if 'HeavenlyCloudShell.Networking type' in self.attributes else None

    @networking_type.setter
    def networking_type(self, value):
        """
        networking type that the cloud provider implements- L2 networking (VLANs) or L3 (Subnets)
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.Networking type'] = value

    @property
    def region(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.Region'] if 'HeavenlyCloudShell.Region' in self.attributes else None

    @region.setter
    def region(self, value=''):
        """
        The public cloud region to be used by this cloud provider.
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.Region'] = value

    @property
    def networks_in_use(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.Networks in use'] if 'HeavenlyCloudShell.Networks in use' in self.attributes else None

    @networks_in_use.setter
    def networks_in_use(self, value=''):
        """
        Reserved network ranges to be excluded when allocated sandbox networks (for cloud providers with L3 networking). The syntax is a comma separated CIDR list. For example "10.0.0.0/24, 10.1.0.0/26"
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.Networks in use'] = value

    @property
    def vlan_type(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.VLAN Type'] if 'HeavenlyCloudShell.VLAN Type' in self.attributes else None

    @vlan_type.setter
    def vlan_type(self, value='VLAN'):
        """
        whether to use VLAN or VXLAN (for cloud providers with L2 networking)
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.VLAN Type'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class HeavenlyCloudAngelDeployment(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype HeavenlyCloudAngelDeployment
        """
        result = HeavenlyCloudAngelDeployment(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'HeavenlyCloudAngelDeployment'

    @property
    def wing_count(self):
        """
        :rtype: float
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.wing_count'] if 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment.wing_count' in self.attributes else None

    @wing_count.setter
    def wing_count(self, value):
        """
        
        :type value: float
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.wing_count'] = value

    @property
    def flight_speed(self):
        """
        :rtype: float
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.flight_speed'] if 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment.flight_speed' in self.attributes else None

    @flight_speed.setter
    def flight_speed(self, value):
        """
        
        :type value: float
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.flight_speed'] = value

    @property
    def cloud_size(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.cloud_size'] if 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment.cloud_size' in self.attributes else None

    @cloud_size.setter
    def cloud_size(self, value):
        """
        
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.cloud_size'] = value

    @property
    def cloud_image_id(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.cloud_image_id'] if 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment.cloud_image_id' in self.attributes else None

    @cloud_image_id.setter
    def cloud_image_id(self, value):
        """
        
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.cloud_image_id'] = value

    @property
    def autoload(self):
        """
        :rtype: bool
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.Autoload'] if 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment.Autoload' in self.attributes else None

    @autoload.setter
    def autoload(self, value=True):
        """
        Whether to call the autoload command during Sandbox setup
        :type value: bool
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.Autoload'] = value

    @property
    def wait_for_ip(self):
        """
        :rtype: bool
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.Wait for IP'] if 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment.Wait for IP' in self.attributes else None

    @wait_for_ip.setter
    def wait_for_ip(self, value=True):
        """
        if set to false the deployment will not wait for the VM to get an IP address
        :type value: bool
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudAngelDeployment.Wait for IP'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value


class HeavenlyCloudManDeployment(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'HeavenlyCloudShell.HeavenlyCloudManDeployment'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype HeavenlyCloudManDeployment
        """
        result = HeavenlyCloudManDeployment(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'HeavenlyCloudManDeployment'

    @property
    def weight(self):
        """
        :rtype: float
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.weight'] if 'HeavenlyCloudShell.HeavenlyCloudManDeployment.weight' in self.attributes else None

    @weight.setter
    def weight(self, value):
        """
        
        :type value: float
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.weight'] = value

    @property
    def height(self):
        """
        :rtype: float
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.height'] if 'HeavenlyCloudShell.HeavenlyCloudManDeployment.height' in self.attributes else None

    @height.setter
    def height(self, value):
        """
        
        :type value: float
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.height'] = value

    @property
    def cloud_size(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.cloud_size'] if 'HeavenlyCloudShell.HeavenlyCloudManDeployment.cloud_size' in self.attributes else None

    @cloud_size.setter
    def cloud_size(self, value):
        """
        
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.cloud_size'] = value

    @property
    def cloud_image_id(self):
        """
        :rtype: str
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.cloud_image_id'] if 'HeavenlyCloudShell.HeavenlyCloudManDeployment.cloud_image_id' in self.attributes else None

    @cloud_image_id.setter
    def cloud_image_id(self, value):
        """
        
        :type value: str
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.cloud_image_id'] = value

    @property
    def autoload(self):
        """
        :rtype: bool
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.Autoload'] if 'HeavenlyCloudShell.HeavenlyCloudManDeployment.Autoload' in self.attributes else None

    @autoload.setter
    def autoload(self, value=True):
        """
        Whether to call the autoload command during Sandbox setup
        :type value: bool
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.Autoload'] = value

    @property
    def wait_for_ip(self):
        """
        :rtype: bool
        """
        return self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.Wait for IP'] if 'HeavenlyCloudShell.HeavenlyCloudManDeployment.Wait for IP' in self.attributes else None

    @wait_for_ip.setter
    def wait_for_ip(self, value=True):
        """
        if set to false the deployment will not wait for the VM to get an IP address
        :type value: bool
        """
        self.attributes['HeavenlyCloudShell.HeavenlyCloudManDeployment.Wait for IP'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

# region Deployment model

# deployment path properties(in deployment-path.yaml) should be represented in a matching class
# injected to DriverRequestParser.
# then retrieved from  deploy_app_action , like this:
# deploy_model = deploy_app_action.actionParams.deployment.customModel
# in our example deploy_model will be either DeployAngelModel or DeployManModel

# to see how injecting, parsing works, look at driver.py __init__ method for example

class HeavenlyCloudAngelDeploymentModel(object):
    __deploymentModel__ = 'HeavenlyCloudShell.HeavenlyCloudAngelDeployment'

    def __init__(self, attributes):
        self.wing_count = ''
        self.flight_speed = ''
        self.cloud_name = ''
        self.cloud_size = ''
        self.cloud_image_id = ''
        self.autoload = ''

        for k, v in attributes.iteritems():
            try_set_attr(self, to_snake_case(self.remove_deployment_prefix(k)), v)

    # attributes key convention is __deploymentModel__.attribute_name
    # e.g HeavenlyCloudShell.HeavenlyCloudAngelDeployment.wing_count
    def remove_deployment_prefix(self, key):
        return key[len(HeavenlyCloudAngelDeploymentModel.__deploymentModel__) + 1:]

class HeavenlyCloudManDeploymentModel(object):
    __deploymentModel__ = 'HeavenlyCloudShell.HeavenlyCloudManDeployment'

    def __init__(self, attributes):
        self.weight = ''
        self.height = ''
        self.cloud_size = ''
        self.cloud_image_id = ''
        self.autoload = ''
        self.wait_for_ip = ''

        for k, v in attributes.iteritems():
            try_set_attr(self, to_snake_case(self.remove_deployment_prefix(k)), v)

    # attributes key convetion is __deploymentModel__.attribute_name
    # e.g HeavenlyCloudShell.HeavenlyCloudManDeployment.height
    def remove_deployment_prefix(self, key):
        return key[len(HeavenlyCloudManDeploymentModel.__deploymentModel__) + 1:]



class Cloud(object):
    def __init__(self, size):
        self.size = size

class HeavenResidentInstance(object):

    def __init__(self, name, descrpition, image, cloud, id, private_ip, public_ip):
        self.name = name
        self.cloud = cloud
        self.image = image
        self.descrpition = descrpition
        self.id = id
        self.private_ip = private_ip
        self.public_ip = public_ip
