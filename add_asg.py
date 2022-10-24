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

def create_launch_configuration():
    response = client.create_launch_configuration(
        LaunchConfigurationName='myLaunchConfig',
        ImageId='ami-085925f297f89fce1',
        KeyName='weather_key',
        SecurityGroups=[
        'sg-056bed241ce2ffcdf',
        ],
        InstanceType='t2.micro',
        InstanceId='i-0204b6172820676a8'
        )
    print(response)

def delete_auto_scaling_group():
    response = client.delete_auto_scaling_group(
    AutoScalingGroupName='myASG',
    ForceDelete=True
    )

def create_auto_scaling_group():
    response = client.create_auto_scaling_group(
    AutoScalingGroupName='myASG',
    LaunchConfigurationName='myLaunchConfig',
    MinSize=1,
    MaxSize=5,
    DefaultCooldown=300,
    AvailabilityZones=[
        'us-east-1a', 'us-east-1b'
    ],
    HealthCheckType='EC2',
    TerminationPolicies=[
        'OldestInstance',
    ],
)
    print(response)

def create_auto_scaling_policy():
    response = client.put_scaling_policy(
        AutoScalingGroupName='myASG',
        PolicyName='ScaleOutPolicy',
        AdjustmentType='ChangeInCapacity',
        ScalingAdjustment=1,
        Cooldown=300,
    )
    print(response)

def describe_scaling_activities():
    response=client.describe_scaling_activities(AutoScalingGroupName="myASG")
    for a in response["Activities"]:
        print(a)
    response=client.describe_policies(AutoScalingGroupName="myASG")
    print(response)


if __name__ == "__main__":
    client = boto3.Session(region_name='us-east-1').client('autoscaling',aws_access_key_id="your-access-key-id",
    aws_secret_access_key="your-secret-access-key")
