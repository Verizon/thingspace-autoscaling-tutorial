'''
Copyright 2022 Verizon

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import boto3

#Delete alarm
def delete_alarm():
    cloudwatch.delete_alarms(
        AlarmNames=['Active_ThingSpace_Connections'],
    )


# Create alarm
def create_alarm():
    cloudwatch.put_metric_alarm(
        AlarmName='Radis_Threshold_Reached',
        AlarmActions=['arn:aws:autoscaling:us-east-1:387420507912:scalingPolicy:4beb1dae-3a3f-494d-acba-2c91ec55c22b:autoScalingGroupName/myASG:policyName/ScaleOutPolicy'],
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='ThingspaceGeoRadius',
        Namespace='5GEdgeTestApp',
        Period=60,
        Statistic='Average',
        Threshold=50,
        AlarmDescription='Alarm when number of ThingSpace device approaches georadius threshold to Wavelength Zone',
        Dimensions=[
            {'Name': 'Application',
            'Value': 'test_app' },
            {'Name': 'Instance',
            'Value': 'test-instance'},
        ],
        Unit='Count'
    )

# Describe alarm
def describe_alarm():
    response = cloudwatch.describe_alarms(
        AlarmNames=[
        'Active_ThingSpace_Connections',
        ])
    print(response)


if __name__ == "__main__":
    cloudwatch = boto3.Session(region_name='us-east-1').client('cloudwatch',
    aws_access_key_id="your-access-key-id",
    aws_secret_access_key="your-secret-access-key")
    create_alarm()
