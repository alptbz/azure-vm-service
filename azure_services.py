import hashlib
import json
import os
from datetime import datetime
from typing import List
from azure.communication.email import EmailClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.v2023_07_01.models import VirtualMachine
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode


class AzureVm:

    def __init__(self, name: str, public_ip: str, username: str, password: str):
        self.password = password
        self.username = username
        self.public_ip = public_ip
        self.name = name

    def __str__(self):
        return f"{self.name} {self.username}@{self.public_ip} {self.password}"

    def __repr__(self):
        return self.__str__()


class AzureService:

    def __init__(self, resource_group_name: str, default_username: str = "azureuser"):
        self.default_username = default_username
        self.resource_group_name = resource_group_name
        self.credential = DefaultAzureCredential()
        self.subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        self.password_secret = os.environ["PASSWORD_SECRET"]
        self.email_endpoint = os.environ["EMAIL_ENDPOINT"]
        self.email_senderaddress = os.environ["EMAIL_SENDER"]

    def send_email(self, to, subject, content):
        client = EmailClient(self.email_endpoint, DefaultAzureCredential())

        message = {
            "content": {
                "subject": subject,
                "plainText": content,
            },
            "recipients": {
                "to": [
                    {
                        "address": to,
                        "displayName": to
                    }
                ]
            },
            "senderAddress": self.email_senderaddress
        }

        poller = client.begin_send(message)
        poller.wait()

    def delete_vm(self, vm_name):
        resource_client = ResourceManagementClient(self.credential, self.subscription_id)

        resource_list = list(resource_client.resources.list_by_resource_group(self.resource_group_name,
                                                                            expand="createdTime,changedTime"))

        resource_types_not_to_delete = ["Microsoft.Compute/disks", "Microsoft.Compute/virtualMachines",
                                        'Microsoft.Network/networkInterfaces']

        resource_to_delete = [x for x in resource_list if
                              x.type not in resource_types_not_to_delete and x.name.startswith(vm_name)]

        vms = [x for x in resource_list if x.type == "Microsoft.Compute/virtualMachines" and x.name.startswith(vm_name)]

        for vm in vms:
            delete_req = resource_client.resources.begin_delete_by_id(vm.id, "2022-11-01")
            delete_req.wait()

        for res in resource_to_delete:
            delete_req = resource_client.resources.begin_delete_by_id(res.id, "2022-11-01")
            delete_req.wait()

    def delete_all(self) -> List[str]:
        resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        resource_list = list(resource_client.resources.list_by_resource_group(self.resource_group_name,
                                                                              expand="createdTime,changedTime"))

        deleted_vm_names = []
        vms = [x for x in resource_list if x.type == "Microsoft.Compute/virtualMachines"]

        for vm in vms:
            deleted_vm_names.append(vm.name)
            self.delete_vm(vm.name)

        return deleted_vm_names

    def list(self) -> List[AzureVm]:
        resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        network_client = NetworkManagementClient(self.credential, self.subscription_id)
        compute_client = ComputeManagementClient(self.credential, self.subscription_id)

        resource_list = list(resource_client.resources.list_by_resource_group(self.resource_group_name,
                                                                            expand="createdTime,changedTime"))

        vms = [x for x in resource_list if x.type == "Microsoft.Compute/virtualMachines"]

        azureVms:List[AzureVm] = []

        for vm in vms:
            vm_info: VirtualMachine = compute_client.virtual_machines.get(self.resource_group_name, vm.name)
            publicIp_info = network_client.public_ip_addresses.get(self.resource_group_name, f"{vm.name}-ip")
            azureVms.append(AzureVm(vm.name, publicIp_info.ip_address, self.default_username,
                                    self.gen_password(vm.name, vm_info.time_created)))

        return azureVms

    def create_vm(self, vm_name):
        password = self.gen_password(vm_name, datetime.now())

        resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        network_client = NetworkManagementClient(self.credential, self.subscription_id)

        with open("armtemplates/template.json", "r") as template_file:
            template_body = json.load(template_file)

        with open("armtemplates/parameters.json", "r") as parameter_file:
            parameter_body = json.load(parameter_file)["parameters"]

        fieldsToReplace = ["networkInterfaceName", "networkSecurityGroupName", "virtualNetworkName",
                           "publicIpAddressName", "virtualMachineName", "virtualMachineComputerName"]

        for field in fieldsToReplace:
            parameter_body[field]["value"] = parameter_body[field]["value"].replace("{machine-name}", vm_name)

        parameter_body["adminPassword"]["value"] = password
        parameter_body["adminUsername"]["value"] = self.default_username

        rg_deployment_result = resource_client.deployments.begin_create_or_update(
            self.resource_group_name,
            f"{vm_name}Deployment",
            {
                "properties": {
                    "template": template_body,
                    "parameters": parameter_body,
                    "mode": DeploymentMode.incremental
                }
            }
        )

        rg_deployment_result.wait()

        public_ip_info = network_client.public_ip_addresses.get(self.resource_group_name, parameter_body["publicIpAddressName"]["value"])

        return AzureVm(vm_name, public_ip_info.ip_address, self.default_username, password)

    def gen_password(self, vm_name, created:datetime):
        wordlist = ['listen', 'fruit', 'report', 'method', 'pride', 'photo', 'class', 'limit', 'slide', 'smoke',
                    'river', 'advice', 'tooth', 'length', 'bunch', 'volume', 'string', 'church', 'split', 'school',
                    'human', 'month', 'switch', 'earth', 'metal', 'visual', 'topic', 'drunk', 'paint', 'blind',
                    'yellow', 'formal', 'devil', 'notice', 'front', 'heart', 'curve', 'local', 'death', 'cross',
                    'drive', 'river', 'split', 'money', 'place', 'friend', 'career', 'mouse', 'point', 'shame', 'green',
                    'piano', 'muscle', 'ideal', 'poetry', 'carry', 'basis', 'truth', 'candle', 'public', 'nerve',
                    'heavy', 'sense', 'handle', 'bonus', 'frame', 'broad', 'watch', 'spirit', 'child', 'manner',
                    'league', 'treat', 'salary', 'press', 'horse', 'debate', 'scene', 'hurry', 'double', 'series',
                    'visual', 'sister', 'hello', 'sector', 'guest', 'chart', 'church', 'class', 'drawer', 'brief',
                    'season', 'court', 'coffee', 'mouth', 'black', 'steak', 'jacket', 'speed', 'great', 'bonus',
                    'native', 'plant', 'woman', 'break', 'medium', 'friend', 'cable', 'assist', 'catch', 'volume',
                    'craft', 'closet', 'model', 'mother', 'death', 'total', 'drive', 'resort', 'reason', 'solid',
                    'month', 'limit', 'candy', 'delay', 'shine', 'piano', 'heart', 'issue', 'bench', 'heart', 'basket',
                    'series', 'divide', 'yellow', 'leave', 'trick', 'assist', 'aspect', 'recipe', 'staff', 'flower',
                    'honey', 'anger', 'glove', 'birth', 'bread', 'escape', 'buddy', 'guard', 'remote', 'tower',
                    'repair', 'family', 'signal', 'buyer', 'pause', 'serve', 'twist', 'month', 'number', 'theme',
                    'union', 'second', 'sister', 'black', 'earth', 'coast', 'editor', 'steak', 'author', 'mouth',
                    'power', 'death', 'theme', 'appeal', 'style', 'trust', 'total', 'clock', 'music', 'anger', 'trick',
                    'wonder', 'sister', 'frame', 'break', 'thing', 'essay', 'matter', 'credit', 'effect', 'tower',
                    'field', 'twist', 'twist', 'brief', 'coffee', 'reveal', 'press', 'smile', 'group', 'search',
                    'sense', 'sound', 'battle', 'person', 'green', 'resist', 'review', 'world', 'royal', 'degree',
                    'window', 'budget', 'parent', 'unique', 'queen', 'photo', 'affect', 'bread', 'scene', 'method',
                    'queen', 'ground', 'check', 'nobody', 'voice', 'wealth', 'sister', 'union', 'change', 'record',
                    'place', 'search', 'shirt', 'south', 'assist', 'muscle', 'mother', 'store', 'delay', 'number',
                    'secret', 'taste', 'shower', 'affect', 'flower', 'joint', 'winter', 'maybe', 'claim', 'union',
                    'sister', 'cousin', 'market']

        result = hashlib.sha256((vm_name + self.password_secret + created.strftime("%j.%Y")).encode("utf-8"))
        digest = result.digest()

        password = "-".join(wordlist[digest[x]] for x in range(4))
        password = password.capitalize()
        password += "-"
        password += str(int(digest[7]))

        return password

