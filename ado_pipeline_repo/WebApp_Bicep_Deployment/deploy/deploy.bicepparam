using 'deploy.bicep'  // main deployment script, execute it to deploy the web app

// NOTE: configure parameters below before executing the deployment script

// Name
param projectId = '' // _ (underscore) is not allowed; length should be 7 characters
param projectName = '' // _ (underscore) is not allowed; max length is 18 characters


// Python
param pathToApp = 'src/app.py'  // path to the main streamlit script, app.py in folder src by default
param pythonVersion = '3.11'

// Web App Deployment
param runFromPackage = 1  // 1 for true, 0 for false; running from archived package cannot directly access local file system, but is much, much faster in deployment
param blobStorage = true // needs to be true if files are saved in the web app and run_from_package is 1

// Server
param existingASPname = ''  // if empty, create new ASP; if not empty, re-use existing ASP in "rg-datascience-utilities"

// Pricing
// See https://azure.microsoft.com/en-us/pricing/details/app-service/linux/#pricing
// Streamlit requires at least B1 tier (due to websockets? See https://learn.microsoft.com/en-us/answers/questions/1470782/how-to-deploy-a-streamlit-application-on-azure-app, but better source needed, or actually test if F1 works now)
param skuProd = 'B1'  // Pricing B1 as default (works, cheap, can be slow); go to B2 or B3 if app is too slow for users
param skuDevtest = 'B1'  // Pricing B1 for devtest, unless app doesn't work, then try B2, then B3
