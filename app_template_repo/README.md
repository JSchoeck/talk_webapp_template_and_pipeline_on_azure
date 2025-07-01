# Template for Python projects

For template version 2.0.0

## Description

This is a template for Python projects that are hosted as an Azure App Service (i.e. a streamlit web app).  
It contains this `readme.md` file with instructions on how to use the template and to use as technical documentation for the app.

## Requirements

- [Anaconda](https://www.anaconda.com/download/success)
- Python >= 3.11
- [Poetry >= 2.0](https://python-poetry.org/docs/#installing-with-the-official-installer)

## How to set up a new project

1. Create a new repository in Azure DevOps and clone it to your VS Code for your project
2. Download template repository to your local machine
3. Extract the content of the downloaded zip file into your new project repository from step 1
4. Adapt the `pyproject.toml` file to your needs (name, version and dependencies & azure environment configuration has to be mentioned here)
5. Create the local virtual environment using poetry (it will be in `.venv`)
6. Commit and push the changes to the new repository
7. Create a new branch called development (switch to it and work only from there when developing, push to main via PRs only)
8. Configure the pipeline file [azure-pipeline-web-app.yml](azure-pipeline-web-app.yml): define files that should not be deployed to the cloud. Optional: adapt the trigger.
9. Commit and push your changes afterwards.  
10. Create a pipeline for your project in ADO.

    > Note: There will only be one pipeline per project, which will push to the devtest or prod instance of your application based on the branch that triggered the run.

    - Go to Azure DevOps Pipelines.
    - Click on New Pipeline -> Azure Repos Git -> <YOUR_REPO> -> Existing azure pipeline YAML file.
    - Select the branch and the pipeline file (`azure-pipeline-web-app.yml`) you want to use. Click on continue.
    - Review that the pipeline is correct and click on Run.
    - From now on, everytime you commit to the development or the main branch your project will be deployed to the devtest or production subscription accordingly.

11. Create the project on [SonarCloud](https://sonarcloud.io), linking the ADO repository.
    - _+_ -> _Analyze new project_ -> Select from ADO repository list
    - Set Quality Gate _NKD_DS_ (Administration -> Quality Gate)
    - Set parameter `sonarCloudQG` in `pyproject.toml` to `true`

12. Add branch policies to use SonarCloud in ADO:  
      - Project Settings -> Repositories -> select your project repo -> Policies -> select `main` branch (repeat for development branch, if wanted)
  
      1. Set up Build Validation  
        - Build Validation -> Add build validation  
        - Select correct build pipeline -> Save

      2. Set up Status Check  
        Note: this is only possible once the pipeline has run at least once, otherwise the status check agent will not be shown in the list!  
        Note: SonarCloud will fail, if the license has no more capacity (lines of code) left.
        - Status Check -> Add status check  
        - Select _SonarCloud/quality gate_  
        - Advanced -> Check _Reset status whenever there are new changes_  
        - Save changes

13. Run the pipeline / Commit new changes to the repository to continuously deploy to the Azure App Service.
14. Distribute app
      - If it doesn't exist yet, ask IT to create a usergroup for the app (i.e. `usergroup_datascience_app_pas_000_demo_app`)
      - Add group `usergroup_datascience_app_ds_team` to allowed users
      - Add the project usergroup to allowed users
      - Create a ticket to add desired users to the project usergroup
      - **Important**: test if anonymous access is blocked by opening the URL of the app in a private browser window

15. Fill out the `readme.md` file with information about the project and delete the template parts.

## Updating dependencies

- To update all dependencies to their latest versions accepted by the specifications in pyproject.toml, run `poetry update` in the project folder  
  (use ´--dry-run´ to check result first; no activated env is necessary).
- Whenever dependencies are modified, run `poetry lock` and `poetry install --no-root` again.  
  This will not update any dependencies to their latest versions, unless their spec was bumped to a higher minimum version in pyproject.toml.
- To remove all packages that are not specified in pyproject.toml from the environment, run `poetry install --no-root --sync`

Note: always commit the updated `poetry.lock` file to the repository.

## Troubleshooting

- If installation fails, follow the manual steps:
    1. Create the local virtual environment (it will be in .venv) by running `poetry env use <PATH>` in the project folder, without any activated virtual environment.  
       Use `conda deactivate` to deactivate any activated virtual environment (might be needed several times).  
       `<PATH>` is the full path to a compatible python environment on your PC (i.e. "`%userprofile%\Anaconda3\envs\python311\python.exe`")
    2. Update dependencies by running `poetry lock`
    3. Run `poetry install --no-root`
- If nkd_utils_lib cannot be found or Authorization fails
  - Get a Personal Access Token (PAT) from Azure DevOps with read rights for Code, Build and Packaging.  
  - Run `poetry config http-basic.<ID> user <PAT>` (replace `<ID>` with an identifier and `<PAT>` with the token from above - try full-access rights, if problem persists)
- If you cannot access Azure Key Vault, install [Azure CLI tools](https://aka.ms/installazurecliwindowsx64) and run `az login` in the command prompt.  
  Note: if you do not have local admin rights, ask IT to install the Azure CLI tools for you.
- If the status check of the SonarCloud Quality Gate returns issues, fix your code and push them to the repo, the analysis will auto-update.  
  You can also check the [SonarCloud](https://sonarcloud.io) dashboard for more information on the issues and to address Security Hotspots.
- If the userguide cannot be found, you neet do remove *.md files from the deletion step in `azure-pipeline-web-app.yml`.
