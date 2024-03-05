# Infrascan Backend

## Setup

1. `cd` into this folder.

2. Add your OpenAI, MapBox and Google Maps API keys to the `data/keys.json` file.
    - In total, as of 2024-03-04, it costs $5 USD per 1000 successful fetch requests to the Infrascan server
    - This is 1/2 of a cent per request.
    - This is at:
        - $5 USD per 1000 requests with the OpenAI's TurboGPT 3.5 API
        - free for 100,000 requests a month with MapBox's Temporary Geocoding API
    - Please confirm this with the appropriate API documentation

3. You should also create an app password for your gmail account of choice to be used as the email verification mailer. Once you have the app password, add it to the `data/keys.json` file under the key `email`. Then, set the constant `EMAIL_ADDRESS` in `constants.py` to be the email address of choice.

4. Install dependancies with `pip install -r ./requirements.txt`.

5. Start the server with `flask run`.