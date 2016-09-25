# Google App Engine: IoT Dashboard with control panel

This repo, I use Google App Engine as backend server to build an IoT dashboard for our ongoing project.
Also add control panel in this app, which means approved users can control some devices connected with
Raspberry Pi.

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
   
## Key step and tool

  
 
