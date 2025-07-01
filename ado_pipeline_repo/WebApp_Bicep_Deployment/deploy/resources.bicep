///////////////////////////////////////////////////////////
// init variables, will be overwritten from deploy.bicep //
///////////////////////////////////////////////////////////
param projectName string
param projectId string
param projectFullName string = '${projectId}-${projectName}'
param location string = resourceGroup().location
param utilitiesResourceGroupName string = 'rg-datascience-utilities'
param existingASPname string = ''
param pathToApp string = 'src/app.py'
param pythonVersion string = '3.11'
param runFromPackage int = 1
param blobStorage bool = false
param skuProd string = 'B1'
param skuDevtest string = 'B1'
param subscriptionId string = subscription().subscriptionId
param subscriptionIdProd string
param environment string = subscriptionId == subscriptionIdProd ? 'production' : 'devtest'
param logAnalyticsWorkspace string = 'log-datascience-dataprocessing'
@secure()
param miGeneralKeyvaultAccess string

var utilitiesResourceGroup = resourceGroup(environment == 'production'
  ? '${utilitiesResourceGroupName}'
  : '${utilitiesResourceGroupName}-dev')

////////////////////////
// Existing resources //
////////////////////////
// Re-use the already existing common log analytics workspace. If it does not yet exist (anymore), create it manually.
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' existing = {
  scope: utilitiesResourceGroup
  name: environment == 'production' ? '${logAnalyticsWorkspace}' : '${logAnalyticsWorkspace}-dev'
}
// Use the specified ASP. If none was specified, create new one further down.
resource existingAppServicePlan 'Microsoft.Web/serverfarms@2023-01-01' existing = if (!empty(existingASPname)) {
  scope: utilitiesResourceGroup
  name: existingASPname
}

///////////////////
// Setup storage //
///////////////////
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = if (blobStorage) {
  // note: Storage account name limited to length between 3 and 24 characters and numbers and lower-case characters. 
#disable-next-line BCP334
  name: environment == 'production'
    ? 'sa${toLower(replace(projectId, '-', ''))}'
    : 'sa${toLower(replace(projectId, '-', ''))}dev'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  tags: {
    Access: 'public'
    Environment: environment
    Owner: 'data science'
  }
  properties: {
    publicNetworkAccess: 'Enabled'  // NOTE: needs to be Enabled for the web app to access the storage account
    accessTier: 'Hot'
    allowBlobPublicAccess: false // false: only reachable with connection string; true: storage is FULLY public!
    minimumTlsVersion: 'TLS1_2'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = if (blobStorage) {
  parent: storageAccount
  name: 'default'
}

resource container 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = if (blobStorage) {
  parent: blobService
  name: 'wa-${storageAccount.name}-container'
  properties: {
    publicAccess: 'None' // 'None', 'Container', 'Blob'; is overwritten by allowBlobPublicAccess from storageAccount
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02-preview' = {
  name: 'wa-${projectFullName}-appinsights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////
// Create new app service plan if no existingASPname is provided, otherwise use the existingASPname //
//////////////////////////////////////////////////////////////////////////////////////////////////////
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = if (empty(existingASPname)) {
  name: environment == 'production' ? 'asp-${projectFullName}' : 'asp-${projectFullName}-dev'
  location: location
  sku: {
    name: environment == 'production' ? skuProd : skuDevtest
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true // true for linux apps
    zoneRedundant: false
  }
}

////////////////////
// Create web app //
////////////////////
resource webApplication 'Microsoft.Web/sites@2024-04-01' = {
  name: environment == 'production' ? 'wa-${projectFullName}' : 'wa-${projectFullName}-dev'
  location: location
  kind: 'app,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '/subscriptions/${subscriptionIdProd}/resourcegroups/${utilitiesResourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mi-keyvault-access': {}
      '/subscriptions/${subscriptionIdProd}/resourcegroups/${utilitiesResourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mi-functionApp-keys-kv-access': {}
    }
  }
  dependsOn: empty(existingASPname) ? [appServicePlan] : [existingAppServicePlan] // make sure the app service plan is created before the web app or the existing ASP has the same name
  tags: {
    Access: 'Public'
    Environment: environment
    Owner: 'data science'
  }
  properties: {
    serverFarmId: empty(existingASPname) ? appServicePlan.id : existingAppServicePlan.id
    siteConfig: {
      alwaysOn: false
      appCommandLine: 'python${pythonVersion} -m streamlit run /home/site/wwwroot/${pathToApp} --server.port 8000 --server.address 0.0.0.0 --server.enableXsrfProtection=false'
      appSettings: [
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '${runFromPackage}'
        }
        {
          name: 'NKD_ENVIRONMENT'
          value: environment
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: applicationInsights.properties.ConnectionString
          // value: 'InstrumentationKey=${applicationInsights.properties.InstrumentationKey};IngestionEndpoint=https://germanywestcentral-1.in.applicationinsights.azure.com/'
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~3' // ~3 for linux (~2 for windows systems)
        }
        {
          name: 'XDT_MicrosoftApplicationInsights_Mode'
          value: 'recommended'
        }
        {
          name: 'AZURE_STORAGE_ACCOUNT_NAME'
          value: blobStorage ? storageAccount.name : ''
        }
        {
          name: '${toUpper(storageAccount.name)}_STORAGE_CONNECTION_STRING'
          value: blobStorage
            ? 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${az.environment().suffixes.storage}'
            : ''
        }
        {
          name: '${toUpper(storageAccount.name)}_STORAGE_CONTAINER'
          value: blobStorage ? container.name : ''
        }
        { name: 'AZURE_MANAGED_IDENTITY_CLIENT_ID'
          value: miGeneralKeyvaultAccess }
      ]
      httpLoggingEnabled: true
      logsDirectorySizeLimit: 35
      linuxFxVersion: 'PYTHON|${pythonVersion}'
      numberOfWorkers: 1
    }
    publicNetworkAccess: 'Enabled'
    httpsOnly: true
  }
}

//////////////////////////////////////
// Add Microsoft indentity provider //
//////////////////////////////////////
// WARNING: This will block all access to the web app until the identity provider is configured.
//          If the restriction is lifted, the web app will be accessible to everyone on the internet!
// Readme.md in the template repository on how to provide access to users:
// https://nkdit.visualstudio.com/Data%20Science/_git/PAS_000_demo_app?path=README.md
resource authsettings 'Microsoft.Web/sites/config@2024-04-01' = {
  parent: webApplication
  name: 'authsettingsV2'
  properties: {
    identityProviders: {
      legacyMicrosoftAccount: {
        enabled: true
      }
    }
    globalValidation: {
      requireAuthentication: true
      unauthenticatedClientAction: 'RedirectToLoginPage'
    }
  }
}
