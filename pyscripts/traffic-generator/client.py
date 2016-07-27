import requests, time

if __name__ == "__main__":
	while True:
		# request every 30 seconds
		r = requests.get("http://10.10.2.225:8000/", headers={
			"content-type": "text",
			"randomKey": "randomVal",
		})

		time.sleep(30)