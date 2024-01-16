from pprint import pprint
from typing import List

import typer
import azure_services
from dotenv import load_dotenv
import helper

load_dotenv()

app = typer.Typer()


@app.command(help="list alls vms with credentials", name="list")
def list_vms():
    azure_service = azure_services.AzureService("LabVms")
    list_of_vms = azure_service.list()
    pprint(list_of_vms)
    print(f"Found {len(list_of_vms)} vms")


@app.command(help="create new vm and send credentials to email", name="create")
def create_vm(emails: List[str]):
    i = 0
    total = len(emails)
    for email in emails:
        vm_name = helper.generate_vm_name_out_of_email(email)
        azure_service = azure_services.AzureService("LabVms")
        print(f"Creating VM {vm_name}...")
        azure_vm = azure_service.create_vm(vm_name)
        print(f"Sending E-mail for {vm_name} to {email}...")
        azure_service.send_email(email, "Your VM Credentials", str(azure_vm))
        i += 1
        print(f"Done {i}/{total}")



@app.command(help="delete single or multiple vms", name="delete")
def delete(vm_names: List[str]):
    i = 0
    total = len(vm_names)
    for vm_name in vm_names:
        azure_service = azure_services.AzureService("LabVms")
        i += 1
        print(f"Deleting {vm_name}...")
        if azure_service.delete_vm(vm_name):
            print(f"Done {i}/{total}")
        else:
            print(f"nothing to delete {i}/{total}")


@app.command(help="delete all vms in resource group", name="delete-all")
def delete_all():
    azure_service = azure_services.AzureService("LabVms")
    print("Deleting...")
    deleted = azure_service.delete_all()
    print("Done. Deleted:")
    pprint(deleted)


if __name__ == "__main__":
    app()