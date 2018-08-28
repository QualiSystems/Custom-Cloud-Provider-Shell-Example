import random
import traceback
import uuid
import os
from cloudshell.cp.core.models import *
from data_model import *
from cloudshell.shell.core.driver_context import CancellationContext
from sdk.heavenly_cloud_service import HeavenlyCloudService
import json
from typing import List


def check_cancellation_context_and_do_rollback(cancellation_context):
    """
    :param CancellationContext cancellation_context:
    """
    if cancellation_context.is_cancelled:
        # rollback what we created for current executing command then raise exception
        # HeavenlyCloudService.rollback()
        raise Exception('Operation cancelled')


def check_cancellation_context(cancellation_context):
    """
    :param CancellationContext cancellation_context:
    """
    if cancellation_context.is_cancelled:
        raise Exception('Operation cancelled')


class HeavenlyCloudServiceWrapper(object):

    @staticmethod
    def deploy_angel(context, cloudshell_session, cloud_provider_resource, deploy_app_action, connect_subnet_actions,
                     cancellation_context):

        check_cancellation_context(cancellation_context)

        # deployment_model type : HeavenlyCloudAngelDeploymentModel
        deployment_model = deploy_app_action.actionParams.deployment.customModel

        # generate unique name to avoid name collisions
        vm_unique_name = deploy_app_action.actionParams.appName + '__' + str(uuid.uuid4())[:6]

        input_user = deploy_app_action.actionParams.appResource.attributes['User']
        encrypted_pass = deploy_app_action.actionParams.appResource.attributes['Password']
        decrypted_input_password = cloudshell_session.DecryptPassword(encrypted_pass).Value

        deployed_app_attributes = []

        if not decrypted_input_password:
            decrypted_input_password = HeavenlyCloudService.create_new_password(cloud_provider_resource, input_user,
                                                                                decrypted_input_password)
            # optional
            # deployedAppAttributes contains the attributes on the deployed app
            # use to override attributes default values
            deployed_app_attributes.append(Attribute('Password', decrypted_input_password))

        # convert the ConnectSubnet actions to networking metadata for cloud provider SDK
        network_data = HeavenlyCloudService.prepare_network_for_instance(connect_subnet_actions)

        try:
            # using cloud provider SDK, creating the instance
            vm_instance = HeavenlyCloudService.create_angel_instance(input_user,
                                                                     decrypted_input_password,
                                                                     cloud_provider_resource,
                                                                     vm_unique_name,
                                                                     deployment_model.wing_count,
                                                                     deployment_model.flight_speed,
                                                                     deployment_model.cloud_size,
                                                                     deployment_model.cloud_image_id,
                                                                     network_data)
        except Exception as e:
            return DeployAppResult(actionId=deploy_app_action.actionId, success=False, errorMessage=e.message)

        # Creating VmDetailsData
        vm_details_data = HeavenlyCloudServiceWrapper.extract_vm_details(vm_instance)

        # result must include the action id it results for, so server can match result to action
        action_id = deploy_app_action.actionId

        # optional
        # deployedAppAdditionalData can contain dynamic data on the deployed app
        # similar to AWS tags
        deployed_app_additional_data_dict = {'Reservation Id': context.reservation.reservation_id,
                                             'CreatedBy': str(os.path.abspath(__file__))}

        deploy_result = DeployAppResult(actionId=action_id, success=True, vmUuid=vm_instance.id,
                                        vmName=vm_unique_name,
                                        deployedAppAddress=vm_instance.private_ip,
                                        deployedAppAttributes=deployed_app_attributes,
                                        deployedAppAdditionalData=deployed_app_additional_data_dict,
                                        vmDetailsData=vm_details_data)

        connect_subnet_results = []
        for connect_subnet_action in connect_subnet_actions:
            connect_subnet_results.append(
                ConnectToSubnetActionResult(connect_subnet_action.actionId,
                                            interface=network_data[connect_subnet_action.actionParams.subnetId]))

        check_cancellation_context_and_do_rollback(cancellation_context)

        return [deploy_result].extend(connect_subnet_results)

    @staticmethod
    def deploy_man(context, cloudshell_session, cloud_provider_resource, deploy_app_action, connect_subnet_actions,
                     cancellation_context):

        check_cancellation_context(cancellation_context)

        # deployment_model type : HeavenlyCloudAngelDeploymentModel
        deployment_model = deploy_app_action.actionParams.deployment.customModel

        # generate unique name to avoid name collisions
        vm_unique_name = deploy_app_action.actionParams.appName + '__' + str(uuid.uuid4())[:6]

        input_user = deploy_app_action.actionParams.appResource.attributes['User']
        encrypted_pass = deploy_app_action.actionParams.appResource.attributes['Password']
        decrypted_input_password = cloudshell_session.DecryptPassword(encrypted_pass).Value

        deployed_app_attributes = []

        if not decrypted_input_password:
            decrypted_input_password = HeavenlyCloudService.create_new_password(cloud_provider_resource, input_user,
                                                                                decrypted_input_password)
            # optional
            # deployedAppAttributes contains the attributes on the deployed app
            # use to override attributes default values
            deployed_app_attributes.append(Attribute('Password', decrypted_input_password))

        # convert the ConnectSubnet actions to networking metadata for cloud provider SDK
        network_data = HeavenlyCloudService.prepare_network_for_instance(connect_subnet_actions)

        try:
            # using cloud provider SDK, creating the instance
            vm_instance = HeavenlyCloudService.create_man_instance(input_user, decrypted_input_password, cloud_provider_resource,
                                                                   vm_unique_name,
                                                                   deployment_model.weight,
                                                                   deployment_model.height,
                                                                   deployment_model.cloud_size,
                                                                   deployment_model.cloud_image_id,
                                                                   network_data)
        except Exception as e:
            return DeployAppResult(actionId=deploy_app_action.actionId, success=False, errorMessage=e.message)

        # Creating VmDetailsData
        vm_details_data = HeavenlyCloudServiceWrapper.extract_vm_details(vm_instance)

        # result must include the action id it results for, so server can match result to action
        action_id = deploy_app_action.actionId

        # optional
        # deployedAppAdditionalData can contain dynamic data on the deployed app
        # similar to AWS tags
        deployed_app_additional_data_dict = {'Reservation Id': context.reservation.reservation_id,
                                             'CreatedBy': str(os.path.abspath(__file__))}

        deploy_result = DeployAppResult(actionId=action_id, success=True, vmUuid=vm_instance.id,
                                        vmName=vm_unique_name,
                                        deployedAppAddress=vm_instance.private_ip,
                                        deployedAppAttributes=deployed_app_attributes,
                                        deployedAppAdditionalData=deployed_app_additional_data_dict,
                                        vmDetailsData=vm_details_data)

        connect_subnet_results = []
        for connect_subnet_action in connect_subnet_actions:
            connect_subnet_results.append(
                ConnectToSubnetActionResult(connect_subnet_action.actionId,
                                            interface=network_data[connect_subnet_action.actionParams.subnetId]))

        check_cancellation_context_and_do_rollback(cancellation_context)

        return [deploy_result].extend(connect_subnet_results)

    @staticmethod
    def extract_vm_details(vm_instance):
        """
        :param HeavenResidentInstance vm_instance:
        """
        vm_instance_data = HeavenlyCloudServiceWrapper.extract_vm_instance_data(vm_instance)
        vm_network_data = HeavenlyCloudServiceWrapper.extract_vm_instance_network_data(vm_instance)

        return VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data)

    @staticmethod
    def extract_vm_instance_data(vm_instance):
        """
        :param HeavenResidentInstance vm_instance:
        """
        data = [
            VmDetailsProperty(key='Cloud Size', value='not so big'),
            VmDetailsProperty(key='Instance Name', value='dummy' if not vm_instance else vm_instance.name),
            VmDetailsProperty(key='Hidden stuff', value='something not for UI', hidden=True),
        ]

        return data

    @staticmethod
    def extract_vm_instance_network_data(vm_instance):
        """
        :param HeavenResidentInstance vm_instance:
        """
        network_interfaces = []

        # get networking data from the cloudprovider and for each network interface extract the data we want to
        # expose in cloudshell
        for i in range(2):
            network_data = [
                VmDetailsProperty(key='Device Index', value=str(i)),
                VmDetailsProperty(key='MAC Address', value=str(uuid.uuid4())),
                VmDetailsProperty(key='Speed', value='1KB'),
            ]

            current_interface = VmDetailsNetworkInterface(interfaceId=i, networkId=i,
                                                          isPrimary=i == 0,
                                                          # specifies whether nic is the primary interface
                                                          isPredefined=False,
                                                          # specifies whether network existed before reservation
                                                          networkData=network_data,
                                                          privateIpAddress='10.0.0.' + str(i),
                                                          publicIpAddress='8.8.8.' + str(i))
            network_interfaces.append(current_interface)

        return network_interfaces

    @staticmethod
    def get_vm_details(logger, cloud_provider_resource, cancellation_context, requests_json):

        """
        :param logging.Logger logger:
        :param L2HeavenlyCloudShell cloud_provider_resource:
        :param CancellationContext cancellation_context:
        :param str requests_json:
        :param str vm_id:
        """
        check_cancellation_context(cancellation_context)
        requests = json.loads(requests_json)

        results = []

        for request in requests[u'items']:

            if cancellation_context.is_cancelled:
                break

            vm_name = request[u'deployedAppJson'][u'name']
            vm_uid = request[u'deployedAppJson'][u'vmdetails'][u'uid']
            address = request[u'deployedAppJson'][u'address']

            vm_instance = HeavenlyCloudService.get_instance(cloud_provider_resource, vm_name, vm_uid, address)
            vm_instance_data = HeavenlyCloudServiceWrapper.extract_vm_instance_data(vm_instance)
            vm_network_data = HeavenlyCloudServiceWrapper.extract_vm_instance_network_data(vm_instance)

            # example of reading custom data created via deployed_app_additional_data_dict at delpoy stage
            # created_by = next((deployed_app_additional_data['value'] for deployed_app_additional_data in request[u'deployedAppJson'][u'vmdetails'][u'vmCustomParams'] if
            #                    deployed_app_additional_data['name'] == 'CreatedBy'), None)
            # if created_by:
            #     vm_instance_data.append(VmDetailsProperty(key='CreatedBy',value=created_by))

            # TODO when prepare connectivity is finished uncomment
            # currently we get error: Check failed because resource is connected to more than one subnet, while reservation doesn't have any subnet services
            # result = VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data, appName=vm_name)
            result = VmDetailsData(vmInstanceData=vm_instance_data, vmNetworkData=vm_network_data, appName=vm_name)
            results.append(result)

            check_cancellation_context(cancellation_context)

        return results

    @staticmethod
    def power_on(cloud_provider_resource, vm_id):
        """
         :param L2HeavenlyCloudShell cloud_provider_resource:
         :param str vm_id:
         """
        HeavenlyCloudService.power_on(cloud_provider_resource, vm_id)

    @staticmethod
    def power_off(cloud_provider_resource, vm_id):
        """
        :param L2HeavenlyCloudShell cloud_provider_resource:
        :param str vm_id:
        """
        HeavenlyCloudService.power_off(cloud_provider_resource, vm_id)

    @staticmethod
    def remote_refresh_ip(cloud_provider_resource, cancellation_context, cloudshell_session, resource_full_name, vm_id,
                          deployed_app_private_ip, deployed_app_public_ip):
        """
        :param L2HeavenlyCloudShell cloud_provider_resource:
        :param CancellationContext cancellation_context:
        :param CloudShellAPISession cloudshell_session:
        :param str resource_full_name:
        :param str vm_id:
        :param str deployed_app_private_ip:
        :param str deployed_app_public_ip:
        """

        check_cancellation_context(cancellation_context)

        curr_ip = HeavenlyCloudService.remote_refresh_ip(cloud_provider_resource, cancellation_context,
                                                         resource_full_name, vm_id)

        if deployed_app_private_ip != curr_ip:
            cloudshell_session.UpdateResourceAddress(resource_full_name, curr_ip)

        if not deployed_app_public_ip:
            cloudshell_session.SetAttributeValue(resource_full_name, "Public IP",
                                                 '1.1.1.{}'.format(str(random.randint(1, 253))))

        check_cancellation_context_and_do_rollback(cancellation_context)

    @staticmethod
    def delete_instance(cloud_provider_resource, vm_id):
        HeavenlyCloudService.delete_instance(cloud_provider_resource, vm_id)

    # region L2 methods
    #
    # @staticmethod
    # def connect(logger, cloud_provider_resource, set_vlan_action):
    #     """
    #     :param logging.Logger logger:
    #     :param L2HeavenlyCloudShell cloud_provider_resource:
    #     :param SetVlan set_vlan_action:
    #     :return:
    #     :rtype: SetVlanResult
    #     """
    #     try:
    #         vnic_name = '' if not 'Vnic Name'  in set_vlan_action.customActionAttributes else set_vlan_action.customActionAttributes['Vnic Name']
    #
    #         logger.info('requested vnic name: ' + vnic_name)
    #         interface_id = HeavenlyCloudService.connect_vlan(cloud_provider_resource, set_vlan_action)
    #
    #         return SetVlanResult(actionId=set_vlan_action.actionId, success=True,infoMessage=vnic_name + ' requested', updatedInterface=interface_id)
    #     except Exception as e:
    #         return SetVlanResult(actionId=set_vlan_action.actionId, success=False, errorMessage=traceback.format_exc())
    #
    # @staticmethod
    # def connect_all(logger, cloud_provider_resource, set_vlan_actions):
    #     """
    #     :param logging.Logger logger:
    #     :param L2HeavenlyCloudShell cloud_provider_resource:
    #     :param [SetVlan] set_vlan_actions:
    #     :return:
    #     :rtype: [SetVlanResult]
    #     """
    #
    #     # vlan_type = cloud_provider_resource.vlan_type
    #     # vlan_type "VLAN" : cloudshell will allow VLAN ids in the 2-4096 range
    #     # vlan_type "XVLAN"  cloudshell will allow VLAN ids to be allocated in range 2-16,000,000
    #     # the default value is VLAN
    #     if not set_vlan_actions:
    #         return []
    #
    #     actions_results = []
    #     for set_vlan_action in set_vlan_actions:
    #         actions_results.append(HeavenlyCloudServiceWrapper.connect(logger, cloud_provider_resource, set_vlan_action))
    #
    #     return actions_results
    #
    # @staticmethod
    # def disconnect(cloud_provider_resource, remove_vlan_action):
    #     """
    #     :param L2HeavenlyCloudShell cloud_provider_resource:
    #     :param RemoveVlan remove_vlan_action:
    #     :return:
    #     :rtype: RemoveVlanResult
    #     """
    #
    #     try:
    #
    #         disconnect_interface_id = remove_vlan_action.connectorAttributes['Interface']
    #         vm_instance_id = remove_vlan_action.customActionAttributes['VM_UUID']
    #         HeavenlyCloudService.disconnect_vlan(cloud_provider_resource,disconnect_interface_id, vm_instance_id)
    #
    #         return RemoveVlanResult(actionId=remove_vlan_action.actionId, success=True, updatedInterface=disconnect_interface_id)
    #     except Exception as e:
    #         return RemoveVlanResult(actionId=remove_vlan_action.actionId, success=False,errorMessage=traceback.format_exc())
    #
    #
    # @staticmethod
    # def disconnect_all(logger, cloud_provider_resource, remove_vlan_actions):
    #     """
    #     :param logging.Logger logger:
    #     :param L2HeavenlyCloudShell cloud_provider_resource:
    #     :param [RemoveVlan] remove_vlan_actions:
    #     :return:
    #     :rtype: [RemoveVlanResult]
    #     """
    #
    #     if not remove_vlan_actions:
    #         return []
    #
    #     actions_results = []
    #
    #     for remove_vlan_action in remove_vlan_actions:
    #         actions_results.append(HeavenlyCloudServiceWrapper.disconnect(cloud_provider_resource, remove_vlan_action))
    #
    #     return actions_results
    #
    # # endregion L2 methods

    # region L3 methods
    @staticmethod
    def prepare_sandbox_infra(logger, cloud_provider_resource, prepare_infa_action, create_keys_action,
                              prepare_subnet_actions, cancellation_context):
        """
        :param logging.Logger logger:
        :param HeavenlyCloudShell cloud_provider_resource:
        :param PrepareCloudInfra prepare_infa_action:
        :param CreateKeys create_keys_action:
        :param List[PrepareSubnet] prepare_subnet_actions:
        :param CancellationContext cancellation_context:
        :return:
        :rtype:
        """

        results = []

        check_cancellation_context_and_do_rollback(cancellation_context)

        cidr = prepare_infa_action.actionParams.cidr

        try:
            # handle PrepareInfraAction - extract sandbox CIDR and create/allocate a network in the cloud provider with
            # an address range of the provided CIDR
            logger.info("Received CIDR {0} from server".format(cidr))

            HeavenlyCloudService.prepare_infra(cloud_provider_resource, cidr)

            results.append(PrepareCloudInfraResult(prepare_infa_action.actionId))
        except:
            logger.error(traceback.format_exc())
            results.append(PrepareCloudInfraResult(prepare_infa_action.actionId,
                                                   success=False,
                                                   errorMessage=traceback.format_exc()))

        check_cancellation_context_and_do_rollback(cancellation_context)

        try:
            # handle CreateKeys - generate key pair or get it from the cloud provider and save it in a secure location
            # that will be accessible from the Deploy method
            sandbx_ssh_key = HeavenlyCloudService.get_or_create_ssh_key()
            results.append(CreateKeysActionResult(create_keys_action.actionId, accessKey=sandbx_ssh_key))
        except:
            logger.error(traceback.format_exc())
            results.append(CreateKeysActionResult(create_keys_action.actionId,
                                                  success=False,
                                                  errorMessage=traceback.format_exc()))

        check_cancellation_context_and_do_rollback(cancellation_context)

        # handle PrepareSubnetsAction
        for action in prepare_subnet_actions:
            try:
                subnet_id = HeavenlyCloudService.prepare_subnet(action.actionParams.cidr,
                                                                action.actionParams.isPublic,
                                                                action.actionParams.subnetServiceAttributes)
                results.append(PrepareSubnetActionResult(action.actionId, subnet_id=subnet_id))
            except:
                logger.error(traceback.format_exc())
                results.append(PrepareSubnetActionResult(action.actionId,
                                                         success=False,
                                                         errorMessage=traceback.format_exc()))

        check_cancellation_context_and_do_rollback(cancellation_context)

        return results

    @staticmethod
    def cleanup_sandbox_infra(cloud_provider_resource, action):
        """
        :param HeavenlyCloudShell cloud_provider_resource:
        :param CleanupNetwork action:
        :return:
        """
        # this is the place were we remove all sandbox infra resources from the cloud provider like network, storage,
        # ssh keys, etc
        return CleanupNetworkResult(actionId=action.actionId)

    # endregion L3 methods