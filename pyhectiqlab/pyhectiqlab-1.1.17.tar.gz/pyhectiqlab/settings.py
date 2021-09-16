import os

if os.environ.get("HECTIQLAB_ENV")=="dev":
	server_url = "http://0.0.0.0:8080"
	app_url = "http://0.0.0.0:3000"
else:
	server_url = "https://hectiq-lab-api-rz3jqlxf4a-ue.a.run.app"
	app_url = "https://lab.hectiq.ai"