import azure_services
from dotenv import load_dotenv
import helper

load_dotenv()

azure_service = azure_services.AzureService("LabVms")

email = input("E-mail?")
vm_name = helper.generate_vm_name_out_of_email(email)
print(f"Creating VM {vm_name}...")
azure_vm = azure_service.create_vm(vm_name)
print("Done")

print(f"Sending E-mail for {vm_name} to {email}...")
azure_service.send_email(email, "Your VM Credentials", str(azure_vm))
print("Done")

