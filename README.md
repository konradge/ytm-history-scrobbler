## Setup
First, you need an API-Key for the [Youtube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=moonlit-nature-311015). Paste the Key into `src/.env`.
Additionally, [sqlite](https://sqlite.org/) needs to be installed.

Now, you can activate the Python venv:
```sh
    cd src
    python3 -m venv .venv 
    source .venv/bin/activate 
    pip install -r requirements.txt
```

## Get your data
To get the Watch-Histories Data, you first need to download your Youtube Watch-History. This can be done [here](https://takeout.google.com/). Make sure, to (only) select `YouTube und YouTube Music > Verlauf` and `JSON` as format. Then, run the script:
```sh
    python run.py <JSON-File> <Path to the DB file>
```
Running the script multiple times merges together all the history-entries while omitting duplicates.