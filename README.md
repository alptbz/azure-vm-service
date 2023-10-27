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

## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a> and [GNU GENERAL PUBLIC LICENSE version 3](https://www.gnu.org/licenses/gpl-3.0.en.html). If there are any contradictions between the two licenses, the Attribution-NonCommercial-ShareAlike 4.0 International license governs. 