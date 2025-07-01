targetScope='subscription'

/////////////////////////////////////////////////////////////
// init variables, will be used if not set in the pipeline //
/////////////////////////////////////////////////////////////
@maxLength(7)
param projectId string
@maxLength(18)
param projectName string
@allowed(['West Europe', 'Germany West Central'])
param location string = 'West Europe'
param utilitiesResourceGroupName string = 'rg-datascience-utilities'
param pathToApp string = 'src/app.py'
param pythonVersion string = '3.11'
param runFromPackage int = 1
param blobStorage bool = false
param skuProd string = 'B1'
param skuDevtest string = 'B1'
param existingASPname string = ''
param subscriptionIdProd string = ''
param dsManagedIdentityKeyvaultAccessClientId string= ''

//////////////////////////////////
// Get secrets from keyvault    //
//////////////////////////////////
// We will use the keyvault to retrieve its managed identity client id. This client id will be added to the created web app and will provide it access to the keyvault. 
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  scope: resourceGroup(subscriptionIdProd, utilitiesResourceGroupName )
  name: 'kv-datascience-general'
  
}

///////////////////////////
// create resource group //
///////////////////////////
resource newRG 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-${projectId}-${projectName}'
  location: location
  tags: {
    owner: 'data science'
  }
}

/////////////////////////////////////////////////
// create resources (ASP, WebApp, Identity...) //
/////////////////////////////////////////////////
module resources 'resources.bicep' = {
  name: 'resources'
  scope: newRG
  params: {
    projectId: projectId
    projectName: projectName
    location: location
    utilitiesResourceGroupName: utilitiesResourceGroupName
    pathToApp: pathToApp
    pythonVersion: pythonVersion
    runFromPackage: runFromPackage
    blobStorage: blobStorage
    skuProd: skuProd
    skuDevtest: skuDevtest
    existingASPname: existingASPname
    miGeneralKeyvaultAccess: dsManagedIdentityKeyvaultAccessClientId
    subscriptionIdProd: subscriptionIdProd
  }
}
