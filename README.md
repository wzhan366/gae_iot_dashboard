# Google App Engine: IoT Dashboard with control panel

This repo, I use Google App Engine as backend server to build an IoT dashboard for our ongoing project.
Also add control panel in this app, which means approved users can control some devices connected with
Raspberry Pi.

[Sample](https://spheric-mission-143823.appspot.com/)

## Idea
- Web App
  - Use GAE to handle url control, view and model
- Data storage
  - IoT devices ( this part codes is running on Raspberry Pi which is not post yet but it doesn't affact this application)
    - Locally: SQLite
    - Cloud: Bigquery
  - Web App
    - Google Datastore ( A No-SQL database)
- Data share between IoT devices and Web App
 - Use SQS( simple queue service provided by Amazon)
   - Web App push user control info to SQS
   - IoT devices pull from queue and act accrodingly
   - IoT devices submit status to queue and Web App update accordingly
- Dashboard/Data visualization
  - Use plotly plot data at Raspberry Pi
  - Embed graphs at Web App side
   
## Key step and tool

### Step
  - Web App
    - Set up url controls at app.yaml file 
    - Set up page view at each templates
    - Set up page actions at main.py
    - Set up data store at main.py
  - Data share
    - Include boto library which includes all the amazon file to power up SQS service
    - Apply AWS account which gives us API_ID and API_KEY
    - Embed API setting
    - Set up sqs service at main.py
  - Data visualization
    - Embed graph url at each templates
    - Graph url is at your plotly profile
  - Deploy
    - Login gcloud to set up initial setting
    - Using command line 
      > appcfg.py -A 'here is your GCP project ID' -V v1 update .
    
### Tool
  - Boto 
    - Amazon serice library
  - Google Python Client
  - Google cloud SDK
  
### Report
  * A report(word file) gives more information of building this application.
  
  
 
