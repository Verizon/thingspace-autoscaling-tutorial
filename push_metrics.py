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

import sys
import requests
from requests_toolbelt.utils import dump
import pprint
import base64
import json
import tsObjects
import boto3
import random
from math import sin, cos, sqrt, atan2, radians
import time
import json
from datetime import datetime

# Get location for a device collection in ThingSpace
def main():
    device_number="<your_device_number>"
    device_imei="<your_imei>"

    aws_access_key_id="<your_aws_access_key>"
    aws_secret_access_key="<your_aws_access_Secret>"

    # lat/long of Boston Wavelength location
    geofence_lat=39.05
    geofence_lon=-77.20
    # distance threshold in km
    geofence_dist=250


    # CloudWatch Init
    cloudwatch = boto3.Session(region_name='us-east-1').client('cloudwatch',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)

    myKeys = tsObjects.tsVariables()
    print("\nfetching ThingSpace bearer ...")
    bearer = GetThingSpaceBearer(myKeys)
    if "access_token" in bearer:
        myKeys.tsBearer = bearer["access_token"]
        print("bearer = " + myKeys.tsBearer)
        print("\nfetching UWS token ...")
        token = GetThingSpaceToken(myKeys)
        if "sessionToken" in token:
            myKeys.uwsToken = token["sessionToken"]
            print("token = " + myKeys.uwsToken)

    if len(myKeys.uwsToken) > 0:

        while True:
            locationDevices = tsObjects.coarseRequest(myKeys)
            # in reality, we'd add all devices and calculate each device's distance to the geofence location
            locationDevices.addDevice("354658090360261", "imei" , "2012746071")
            print("\nfetching location results ...")
            output=locationDevices.getLocations(myKeys)


            radius=output[0]['pd']['radius']
            device_lat=output[0]['pd']['x']
            device_lon=output[0]['pd']['y']
            measurementTime=output[0]['pd']['time']
            print(f'Latitude (x): {lat}')
            print(f'Longitude (y): {lon}')
            print(f'Radius (meters): {radius}')
            print(f'Time of reported location: {measurementTime}')

            dist=calculateDistance((device_lat,device_lon),(geofence_lat,geofence_lon))
            if dist <= geofence_dist:
                response = cloudwatch.put_metric_data(
                    MetricData = [
                    {
                    'MetricName': 'ThingspaceGeoRadius',
                    'Dimensions': [
                    {
                        'Name': 'Application',
                        'Value': 'test_app'
                    }
                    ],
                    'Unit': 'Count',
                    # simulate (fake) the number of devices that are within the 'geofence_dist' range
                    'Value': random.randint(50, 200)
                    },
                    ],Namespace = '5GEdgeTestApp')
                print(response)
            time.sleep(1)

            cwStats = cloudwatch.get_metric_data(
              MetricDataQueries=[
                  { 'Id':'testQuery', 'MetricStat': {  'Metric': {
                              'Namespace': '5GEdgeTestApp',
                              'MetricName': 'ThingspaceGeoRadius',
                              'Dimensions': [
                                  {
                                      'Name': 'Application',
                                      'Value': 'test_app'
                                  },
                              ]
                          },
                        'Period': 60,
                        'Stat':'Average'
                       },
                      'ReturnData': True,
                    #   'Period':60
                  },],
                StartTime=datetime(2021, 4, 5),
                EndTime=datetime(2021, 4, 6)

                )
            print(cwStats)



    else:
        print("\nno UWS token.")
    print ("\nDone.")

# https://thingspace.verizon.com/resources/documentation/connectivity/Getting_Started/Getting_Credentials/
def GetThingSpaceBearer(myKeys: tsObjects.tsVariables):
	myUrl = "https://thingspace.verizon.com/api/ts/v1/oauth2/token"
	myKeySecret = myKeys.myKey + ":" + myKeys.mySecret
	myBase64String = base64.b64encode(myKeySecret.encode("ascii"))
	myHeader = {}
	myHeader["Accept"] = "application/json"
	myHeader["Content-Type"] = "application/x-www-form-urlencoded"
	myHeader["Authorization"] = "Basic " + myBase64String.decode("ascii")
	myBody = {}
	myBody["grant_type"] = "client_credentials"
	responseJson = {}
	try:
		response = requests.post(url = myUrl, headers = myHeader, data = myBody)
		if response.status_code == requests.codes.ok:
			responseJson = json.loads(response.text)
		else:
			print(response.content.decode("UTF-8"))
			sys.exit()
	except requests.exceptions.RequestException as e:
		raise SystemExit(e)
	return responseJson

# https://thingspace.verizon.com/resources/documentation/connectivity/API_Reference/Start_Connectivity_Management_Session/
def GetThingSpaceToken(myKeys: tsObjects.tsVariables):
	myUrl = "https://thingspace.verizon.com/api/m2m/v1/session/login"
	myBody = {}
	myBody["username"] = myKeys.uwsUsername
	myBody["password"] = myKeys.uwsPassword
	responseJson = {}
	try:
		response = requests.post(url = myUrl, headers = myKeys.genDefaultHeader(), data = json.dumps(myBody, sort_keys=True))
		if response.status_code == requests.codes.ok:
			responseJson = json.loads(response.text)
		else:
			print(response.content.decode("UTF-8"))
			sys.exit()
	except requests.exceptions.RequestException as e:
		raise SystemExit(e)
	return responseJson


def calculateDistance(location_1,location_2):
    lat1=radians(float(location_1[0]))
    lon1=radians(float(location_1[1]))
    lat2=radians(float(location_2[0]))
    lon2=radians(float(location_2[1]))

    # approximate radius of earth in km
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    print(f'Distance from geofence: {distance} km')
    return distance



if __name__ == "__main__":
	main()
