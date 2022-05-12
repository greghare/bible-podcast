# Bible Podcast

Generates a podcast feed with a new reading from the ESV Bible each day

## 1. Installation

```
git clone https://github.com/greghare/bible-podcast.
pip install feedgen
pip install mutagen
```

```
Create a directory on your web server (can be named whatever you want, e.g. "bible-podcast")
Inside this directory create a directory called "media"
```

## 2. Configuration

- Create an API account and an application at https://api.esv.org/account/create-application/ (must wait for approval)
- Create an ftp user on your web server that maps to the parent directory (e.g. "bible-podcast")
- Copy main.config.example to main.config and edit it to include your ftp server, user id, password, and API key
- Optional: Configure a cronjob to run bible-podcast.py once a day

## 3. Running

If you opted to configure a cronjob, just wait for it to run! Otherwise, to manually run the script:

```
python bible-podcast.py
```

## Other notes...

The files in the "util" directory are used to generate the reading_plan.json file. This only needs to be run once to regenerate the reading plan for the year.
These scripts are rough around the edges, and could use some cleaning up, but were they get the job done.

The ESV API terms do not allow locally storing more than 500 consecutive verses at a time, which is why the script caps this at 500 verses.
