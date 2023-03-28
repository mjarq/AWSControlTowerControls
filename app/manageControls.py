import os
import boto3
import csv
import json


class ControlsManager():

    def __init__(self, controls_config):
        self.controls_config = controls_config
        self.controltower_client = boto3.client('controltower')
        self.controls_list_from_config = []
        self.OUs_list = []
        self.enabled_controls_list_temp = []
        self.enabled_controls_for_OUs = {}


    # Update all the controls state based on config
    def manage_controls(self):
        ## Get the list of conttrols from config
        self.get_controls_list_from_config()

        ## Extract the unique list of OUs
        self.OUs_list = set([x[3] for x in self.controls_list_from_config])

        ## Parse through list of OUs and extract the list of enabled controls for the OU
        for OU in self.OUs_list:
            self.enabled_controls_list_temp = []
            self.get_enabled_controls(OU)
            self.enabled_controls_for_OUs[OU] = self.enabled_controls_list_temp

        ## Enable or disable control based on the provided state in config file
        for control in self.controls_list_from_config:
            self.update_control(control)


    # Get all the controls state based on config
    def get_controls_list_from_config(self):

        # Pull in Controls List from config file
        with open(self.controls_config) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')            
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    ## this is header, ignore
                    line_count = 1
                    continue
                else:
                    ## Enable or disable control based on the provided state in Controls config file
                    self.controls_list_from_config.append(row)

    ## get a list of enabled controls for the OU
    def get_enabled_controls(self, targetIdentifier, nextToken=None):
        if not nextToken:
            response = self.controltower_client.list_enabled_controls(      
                targetIdentifier=targetIdentifier
            )

            self.enabled_controls_list_temp = self.enabled_controls_list_temp + response['enabledControls']
            next_token = response.get('nextToken', None)
            if next_token:
                self.get_enabled_controls(targetIdentifier, next_token)            
        else:
            response = self.controltower_client.list_enabled_controls(      
                targetIdentifier=targetIdentifier,
                nextToken=nextToken
            )

            self.enabled_controls_list_temp = self.enabled_controls_list_temp + response['enabledControls']
            next_token = response.get('nextToken', None)
            if next_token:
                self.get_enabled_controls(targetIdentifier, next_token)

    
    def update_control(self, control):
        response = ""

        print("Making updates to a control in AWS control tower")

        if (control[2] == "1"): ## this is Control enable operation
            ## check if control is already enabled
            if not (control[0] in [x['controlIdentifier'] for x in self.enabled_controls_for_OUs[control[3]]]): ## it is diabled
                response = self.controltower_client.enable_control(            
                    controlIdentifier=control[0], ##control ARN
                    targetIdentifier=control[3], ##OU ARN
                )
            else:
                response = "Control is already enabled, no action taken"
        else: ## this is Control disable operation            
            if(control[0] in [x['controlIdentifier'] for x in self.enabled_controls_for_OUs[control[3]]]): ## it is enabled
                response = self.controltower_client.disable_control(            
                    controlIdentifier=control[0], ##control ARN
                    targetIdentifier=control[3], ##OU ARN
                )
            else:
                response = "Control is already disabled, no action taken" 

        print(response)

# Main function
def main(event, context):
    controls_config = os.environ['CONTROLS_CONFIG']
    controls_manager = ControlsManager(controls_config)
    controls_manager.manage_controls()

# If this is triggered by the lambda
def controls_handler(event, context):
    main(event, context)

# If we are running this locally
if __name__ == "__main__":
    os.environ['CONTROLS_CONFIG'] = "controls/controls_config.csv"
    main("{}", None)
