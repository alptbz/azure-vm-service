from pprint import pprint
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
def create_vm(email: str):
    vm_name = helper.generate_vm_name_out_of_email(email)
    azure_service = azure_services.AzureService("LabVms")
    print(f"Creating VM {vm_name}...")
    azure_vm = azure_service.create_vm(vm_name)
    print("Done")
    print(f"Sending E-mail for {vm_name} to {email}...")
    azure_service.send_email(email, "Your VM Credentials", str(azure_vm))
    print("Done")


@app.command(help="delete single vm", name="delete")
def delete(vm_name: str):
    azure_service = azure_services.AzureService("LabVms")
    print("Deleting...")
    if azure_service.delete_vm(vm_name):
        print("Done")
    else:
        print("nothing to delete")


@app.command(help="delete all vms in resource group", name="delete-all")
def delete_all():
    azure_service = azure_services.AzureService("LabVms")
    print("Deleting...")
    deleted = azure_service.delete_all()
    print("Done. Deleted:")
    pprint(deleted)


if __name__ == "__main__":
    app()