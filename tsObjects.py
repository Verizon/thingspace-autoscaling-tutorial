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

from marshmallow import Schema, fields
import datetime
import requests
from requests_toolbelt.utils import dump
import json
import sys
import pprint

class tsVariables:
	def __init__(self):
		self.myKey = "<your_thingspace_access_key>"
		self.mySecret = "<your_thingspace_access_secret_key>"
		self.uwsUsername = "<your_thingspace_username>"
		self.uwsPassword = "<your_thingspace_password>"
		self.tsBearer = ""
		self.uwsToken = ""
		#Account number
		self.account = "<your_verizon_thingspace_accountnumber>"
		# requests library does not pull local adapter proxy settings; must set and pass in each post, get, etc. when on a corp network
		#self.httpProxy = {}
		#self.httpProxy["http"] = "proxy.address"
		#self.httpProxy["https"] = "proxy.address"
		#self.billCycle = 2

	def genDefaultHeader(self):
		myHeader = {}
		myHeader["Accept"] = "application/json"
		myHeader["Content-Type"] = "application/json"
		myHeader["Authorization"] = "Bearer " + self.tsBearer
		if len(self.uwsToken) > 0:
			myHeader["VZ-M2M-Token"] = self.uwsToken
		return myHeader

class coarseRequestDevice:
	def __init__(self):
		self.id = ""
		self.kind = ""
		self.mdn = ""

class coarseRequest:
	def __init__(self, keys):
		self.accountName = keys.account
		self.accuracyMode = "0"
		self.cacheMode = "2"
		self.deviceList = list()

	def addDevice(self, id, kind, mdn):
		device = coarseRequestDevice()
		device.id = id
		device.kind = kind
		device.mdn = mdn
		self.deviceList.append(device.__dict__)

	# https://thingspace.verizon.com/resources/documentation/location/API_Reference/Get_Device_Locations_synchronous/
	def getLocations(self, myKeys):
		myUrl = "https://thingspace.verizon.com/api/loc/v1/locations"
		try:
			response = requests.post(url = myUrl, headers = myKeys.genDefaultHeader(), data = json.dumps(self.__dict__, sort_keys=True), proxies = myKeys.httpProxy)
			if response.status_code == requests.codes.ok:
				responseJson = json.loads(response.text)
				positionSchema = LocationSchema(many=True)
				try:
					positionCollection = positionSchema.dump(responseJson)
				except ValidationError as e:
					print(e.messages)
					print(e.valid_data)
					sys.exit()
				except TypeError as e:
					print(e)
					sys.exit()
			else:
				print(response.content.decode("UTF-8"))
				sys.exit()
		except requests.exceptions.RequestException as e:
			raise SystemExit(e)
		return positionCollection

class subscriptionStatusRequest:
	def __init__(self, keys):
		self.accountName = keys.account
		self.balance = 0

	# https://thingspace.verizon.com/resources/documentation/location/API_Reference/Get_Subscription_Status/
	def getStatus(self, myKeys):
		myUrl = "https://thingspace.verizon.com/api/loc/v1/subscriptions/" + self.accountName
		try:
			response = requests.get(url = myUrl, headers = myKeys.genDefaultHeader(), proxies = myKeys.httpProxy)
			if response.status_code == requests.codes.ok:
				responseJson = json.loads(response.text)
				statusSchema = SubscriptionStatusSchema()
				try:
					subscriptionStatus = statusSchema.dump(responseJson)
				except ValidationError as e:
					print(e.messages)
					print(e.valid_data)
					sys.exit()
				except TypeError as e:
					print(e)
					sys.exit()
				self.balance = int(responseJson["maxAllowance"]) - int(responseJson["usedAllowance"])
			else:
				print(response.content.decode("UTF-8"))
				sys.exit()
		except requests.exceptions.RequestException as e:
			raise SystemExit(e)
		return subscriptionStatus

PdSchema = Schema.from_dict({'time': fields.Str(), 'utcoffset': fields.Str(),
	'x': fields.Str(), 'y': fields.Str(), 'radius': fields.Str(), 'qos': fields.Boolean()})
ErrorSchema = Schema.from_dict({'time': fields.Str(), 'type': fields.Str(), 'info': fields.Str(), 'utcoffset': fields.Str()})
LocationSchema = Schema.from_dict({'msid': fields.Str(), 'pd': fields.Nested(PdSchema()),
	'error': fields.Nested(ErrorSchema())})

SubscriptionStatusSchema = Schema.from_dict({'accountName': fields.Str(), 'locType': fields.Str(), 'maxAllowance': fields.Str(), 'usedAllowance': fields.Str(), 'purchaseTime': fields.Str()})
