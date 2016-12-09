# README #

Watchdog that monitors **Google Cloud Platform** (GCP) services. Creates a HTML report file which lists the following across all your projects:

*  Compute instances 
*  Identity and Access Management (IAM) 
*  Firewall rules 

This allows you to monitor all your GCP projects in a convenient way. For example, use it to:

* Track running instances (you might have forgotten about)
* Check people's access and roles
* Find open ports 

All put together in a HTML report which can be sent out via email. The report can be customized with a configuration file (*watchdog.yaml*), so certain projects, instances, firewalls etc. can be ignored or highlighted. 


## Installation

Install with: 

```
cd gcp-watchdog/
pip install .
```


## Setup 
1. Create a service account on GCP to use with the gcp-watchdog. You can also use your user account but its good practice to use a service account with a limited scope, especially if you run the watchdog on a compute instance.   

2. Set *browse* permissions on GCP for all the projects you want to include in the report. *Browse* permissions in GCP can be set for either
    1. Each project individually
    2. On the organization level with the organization node. (https://cloud.google.com/resource-manager/docs/quickstart)    

3. Activate Compute Engine for the projects you want to include in the report. (GCP-watchdog requires the Compute Engine to be configured to get information about instances)  

4. Set your service account credentials as environment variable:  
*export GOOGLE_APPLICATION_CREDENTIALS=path_to_json*


5. Create your configuration file (watchdog.yaml). See below for a template.   

6. Optional: If you use the email function to send out an email with the report via Sendgrid, you need to set your Sendgrid api key as environment variable.  
*export SENDGRID_API_KEY=path_to_sendgrid_key* 

7. Run with:
```
gcp-watchgog --config watchdog.yaml
```
   
Create your Sendgrid account here: https://sendgrid.com/, or configure any other email client yourself.

## Options 
send report as email (receivers are specified in watchdog.yaml. Needs email client to be configured in send_email.py):

```
gcp-watchdog --email 
```
Specify the name of the report HTML file:

```
gcp-watchdog --output daily_report.html
```
Don't write HTML report to file:

```
gcp-watchdog --no-output 
```

## Configuration file (watchdog.yaml)
You can configure the report by specifying rules in the config file. Just add keywords to the rules.  

**There are three types of rules:**  

* Notify-rules: Whitelisting (Filters out everything you don't add here. If left empty, everything will be whitelisted)
* Ignore-rules: Blacklisting (Filters out everything you add here)
* Alert-rules: Highlighting (Highlights everything you add here in the report in orange)


You don't have to specify the whole name or string. The watchdog will apply the rule to everything that includes the string. 

Example: 
```
  ignore-zones:  
    name:
      - string:  asia     
```
Will ignore all zones where the string *asia* appears: asia-east1-a, asia-east1-b, asia-northeast1-a ...  


If you add multiple rules for a keyword use the *- string* key:

For example:

```
  ignore-zones:  
    name:
      - string:  us   
      - string:  europe   
```
 
**You will find an example of the configuration file in the *templates* folder**
