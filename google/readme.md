Google cloud steps:

***IMPORTANT***
Don't click 'upgrade' or anything in google cloud - this'll make you go from free trial to paid, and while its fine since there's already safeguards you'll want to avoid any chance of potentially overspending as you could potentially spend lots of money.
https://console.cloud.google.com/billing -> credits to see your remaining credits.

Setup warnings and limits here:
https://console.cloud.google.com/billing/budgets
https://console.cloud.google.com/iam-admin/quotas

If it doesnt work , then enable billing.

---guide starts here---

1. Setup account on google cloud
https://cloud.google.com/free
You'll be asked to provide a credit card but its only for verfiication.
    
    a. Create  a project, name it anything. note down the project id.
    Should look something like this: project-xxxxxxxx-xxxx-xxxx-xxx

***2. Setup vertex api***

Enable all recommended api's under vertex AI
Top left menu, products, vertex AI
https://console.cloud.google.com/vertex-ai/dashboard


***3. Install dependencies***

Create a folder where your config files will be stored, I put mine in C:\Coding\litellm

Open CMD:
```
a. Install Python 3.9> 3.14< if you don't have it already
    winget install Python.Python.3.12

b. Install NodeJS if you don't have it already
    winget install OpenJS.NodeJS

c. Install Google Cloud SDK
    winget install Google.CloudSDK
```
*Close CMD, reopen*

setup openclaude + litellm.
`You can do this in a venv if you like, otherwise just install globally`
```
pip install "litellm[proxy,google]
npm install -g @gitlawb/openclaude
```
Link GCLoud to your computer
```
gcloud auth application-default login
```
Create config.yaml file in your working dir
```
model_list:
  - model_name: gemini-3.1
    litellm_params:
      model: vertex_ai/gemini-3.1-pro-preview
      vertex_project: "project-xxxxxxxx-xxxx-xxxx-xxx"
      vertex_location: "global"

general_settings:
  max_budget: 280
  budget_duration: 30d
```

***Change vertex_project to your project id***


Usage:
Run litellm in a command prompt, do not close. Change config path to your config yaml
```litellm --config C:\Coding\config.yaml```
run openclaude
```openclaude```

setup provider
/provider
add provider (Custom/13)
```
URL: http://localhost:4000/v1
Model: gemini-3.1
api-key: sk-bla
```