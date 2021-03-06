import requests
import random
import json 

class Sdk(object):

	connection = {};
	headers    = {};
	payload    = {};

	def __init__(self, instance_url, token):
		self.payload['user_token'] = ''
		self.payload['params'] = {}
		self.connection['instance_url'] = instance_url
		self.headers = {
			    'content-type':  "application/json",
			    'cache-control': "no-cache",
			    'devless-token': token
			    }
   		
	def addData(self, service, table, data):
		data   = json.dumps({"resource": [ {'name':table,"field":[data] } ]})
		subUrl = '/api/v1/service/{service}/db'.format(service=service)
  		return self.request_processor(data, subUrl, 'POST')

	def getData(self, service, table):
		data   = {}
		params = self.payload['params'] if 'params' in self.payload else ''
		def queryMaker(params):
			queryParams = ''
			for key, value in params.iteritems():
				if(type(value) == list):
					for key_word in value:
						queryParams += "&{key}={key_word}".format(key=key, key_word=key_word)
				else:
					queryParams = "&{key}={value}{queryParams}".format(key=key, value=value,
						queryParams=queryParams)
			return queryParams
		query = queryMaker(params) if params != None else ''	
		subUrl = '/api/v1/service/{service}/db?table={table}{query}'.format(service=service, table=table, query=query)
		return self.request_processor(data, subUrl, 'GET')
	
	def updateData(self, service, table, data):
		params = self.payload['params']['where'][0]
		data   = json.dumps({"resource":[{"name":table,"params":[{"where":params,"data":[data]}]}]})
		subUrl = '/api/v1/service/{service}/db'.format(service=service)
		return self.request_processor(data, subUrl, 'PATCH')

	def deleteData(self, service, table):
		params = self.payload['params']['where'][0]
		data   = json.dumps({"resource":[{"name":table,"params":[{"where":params,"delete":"true"}]}]})
		subUrl = '/api/v1/service/{service}/db'.format(service=service)
		return self.request_processor(data, subUrl, 'DELETE')

	def call(self, service, method, params={}):
		call_id = random.randint(1, 200000)
		params  = json.dumps({ "jsonrpc":"2.0","method":service,"id":call_id,"params":params})
		subUrl = "/api/v1/service/{service}/rpc?action={method}".format(service=service, method=method)
		return self.request_processor(params, subUrl, 'POST')

	def setUserToken(self, token):
		self.headers['devless-user-token'] = token
		return self 

	def where(self, column, value):
		param = "{column},{value}".format(column=column, value=value)
		self.bindToParams('where', param)
		return self

	def offset(self, value):
		self.bindToParams('offset', value)
		return self

	def orderBy(self, value):
		self.bindToParams('orderBy', value)
		return self

	def size(self, value):
		self.bindToParams('size', value)
		return self

	def bindToParams(self, methodName, args):
		if methodName == 'where':
			self.payload['params'][methodName] =  [] if not methodName in self.payload['params'] else self.payload['params'][methodName]
			self.payload['params'][methodName].append(args)
		else:
			self.payload['params'][methodName] = None if methodName in self.payload['params'] else ''
			self.payload['params'][methodName] = args;

	def seq_iter(self, obj):
	    return obj if isinstance(obj, list) else iteritems(obj)		

	def request_processor(self, data, subUrl, method):
		url = "{instance_url}{subUrl}".format(
			instance_url = self.connection['instance_url'], subUrl
			= subUrl)
		response = requests.request(method,
		 url, data=data, headers=self.headers)
		output_text = response.text
		start  = output_text.find('{')
		end    = output_text.rfind('}')
		json_output = output_text[start:end+1] if start is not -1 or end is not -1 else output_text
		return json.loads(json_output)
