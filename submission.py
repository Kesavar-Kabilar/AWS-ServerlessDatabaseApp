import requests
import json

url = '' # REDACTED FOR PRIVACY

payload = {
			"submitterEmail": "", # REDACTED FOR PRIVACY
			"secret": "", # REDACTED FOR PRIVACY
			"dbApi": "" # REDACTED FOR PRIVACY
		}

print(json.dumps(payload))
print("Running the autograder. This might take several seconds...")
r = requests.post(url, data=json.dumps(payload), headers = {"Content-Type": "application/json"})


print(r)
print(r.status_code, r.reason)
print(r.text)
