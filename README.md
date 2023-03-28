# AWS Control Tower Controls Management

This is a sample repo which can be used to manage Controls in AWS Control Tower. The solution provides a way to update (enable/disable) controls across the required OUs in AWS Organisation.

Key solution highlights: 
* The solution uses AWS SDK for Python (Boto3) to interact with AWS Control Tower
* The solution can be used to entrally apply controls across multiple OUs from AWS Control Tower
* The list of controls which need to be updated is maintained as an external config under */controls/controls.csv*
* The solution should be deployed and run in management account which has AWS Control Tower

## Tech Stack

* AWS Cloudformation
* [AWS Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/)
* boto3

## Format of controls config file
The config file which is located at */controls/controls.csv* is a csv file with below columns. This can be updated as required. Any changes made to config file may require updates under *manage_controls()* and *update_control* functions.
```
Control ARN,Control ID,Operation(1 = Enable; 0 = Disable),OU ARN,Control Name,Control Owner
```

## SAM commands
Build the repo:
```
sam build
```

Run locally:
```
sam local invoke ControlsManagerFunction  --event test.json 
```

Push code:
```
sam deploy --guided
```

