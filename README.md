# [Template-based web app and deployment pipeline at an enterprise-ready level on Azure](https://nuernberg.digital/en/events/2025/template-based-web-app-and-deployment-pipeline-at-an-enterprise-ready-level-on-azure)
*How to build a complete web app template, dev environment, and deployment pipeline in an actual enterprise-level Azure cloud.*

Code and slides for my talk at [Nürnberg Digital Festival 2025](https://nuernberg.digital/en)

## Links
- [Nürnberg Digital Festival 2025](https://nuernberg.digital/en)
- [Meetup: Nürnberg Data Science & Artificial Intelligence](https://www.meetup.com/nuernberg-data-science)
- [Meetup Event](https://www.meetup.com/nuernberg-data-science/events/308574638/)
- [Meetup LinkedIn Page](https://www.linkedin.com/company/data-science-ai-nurnberg/)

## Description
In many enterprise environments, deploying a proof-of-concept data app to the cloud remains frustratingly slow and manual. Early user feedback often depends on clunky screen shares or static screenshots. This talk shows how we transformed that process - automating everything from infrastructure provisioning to web app deployment - using a system of pipeline, bicep, and python templates. The result? Stakeholders can interact with a working Streamlit app within minutes of a commit, with no further manual setup required.

We take you with us on our journey from awkward beginnings to an elegant template-based setup, where all steps of the configuration and deployment process are automated. All Azure resources are created without manual steps. And it takes only one bio-break from submitting your work to the repository to the business user being able to test it live. Along the way we share best practices and pitfalls we discovered, as well as how we structure our templates and repositories, both for the web app, as well as the deployment pipeline. At the end, we will deploy a new web app together and explore the workings of the system live.

While the concept will need adoption to other providers, you don't need to use Azure to profit from this talk - all cloud platforms share similar tools and challenges.

### Detailed Outline
#### 1. Motivation
- Why it's hard to get user feedback early and why that is problematic
- Why it's hard to get a real application running early
- What if we could automate app deployment and configuration, or how the NKD data science teams went from awkward to awesome

#### 2. The app creation, deployment, and configuration process
- Struggles and best practices
- Tools that help with consistency and automation
- Handling virtual environments across dev systems and the cloud
- Web app and pipeline repositories and templates

#### 3. The pipeline
- Structure of the stages
- Minimizing manual configuration with file parsing and bicep
- Matching branch and target server
- Automated Azure resource creation using Azure CLI
- App authorization and authentication configuration with more Azure CLI
- Finally, the deployment

#### 4. Show case
- What the setup looks like when it's fully set up
- Deploying an app live

### Key Takeaways
- How to reduce app deployment time from days to minutes using automated templates
- Collaboration setup for small and medium-sized data teams
- Best practices for structuring pipelines and web apps for consistency, security, and scalability
- What not to do: key pitfalls we encountered and how we fixed them

### Target audience
Data or machine learning scientists or engineers in small or medium-sized teams, who want to deploy web apps faster and in a more consistent way. Attendees should be comfortable with python and have basic familiarity with web apps or DevOps principles. While Azure users benefit most, no in-depth knowledge is required - concepts will be explained as we go.
