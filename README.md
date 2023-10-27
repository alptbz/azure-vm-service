# Azure VM Service

Script to create vm and send credentials via E-Mail

# Ressources

 - https://learn.microsoft.com/en-us/cli/azure/ad/app?view=azure-cli-latest#az-ad-app-create
 - https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python
 - https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/deploy-python
 - https://github.com/Azure-Samples/azure-samples-python-management

# Create access token
 - az ad app create --display-name LabVmManager --enable-access-token-issuance true

## .env file
needs to contain:
```shell
AZURE_SUBSCRIPTION_ID=
AZURE_CLIENT_ID=
AZURE_TENANT_ID=
AZURE_CLIENT_SECRET=
PASSWORD_SECRET=
EMAIL_ENDPOINT=
EMAIL_SENDER=
```

`PASSWORD_SECRET` is used to generate deterministic passwords using sha256