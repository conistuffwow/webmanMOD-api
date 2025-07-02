# webmanMOD-api

webmanMOD-api is an api wrapping around Webman MOD. 
You can use it inside websites, etc.

# Running

Install Python 3.13 and install "flask", "requests", then run the app.
To check the API is working, visit http://localhost:8080/api/v1/ping

Make sure your PS3's local IP is set in config.txt.

If you plan to run this on your website, make sure to turn "ALLOW_NOTIFY" and "ALLOW_SYSTEM" to "false" so people can't annoy you while gaming, because people'll definitely use inspect element, lmao.
