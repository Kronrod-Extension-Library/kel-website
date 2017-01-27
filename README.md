Kronrod Extensions Library Website Templates
============================================

Script, template and style files to build the 'Kronrod Extensions Library' website from the data.


Build the website
-----------------

To generate the website, start from this directory and first set up and activate the python virtualenv:

```
virtualenv --python=python3.5 venv
. venv/bin/activate
```

Install the necessary python packages:

```
pip install -r requirements.txt
```

And finally run the build script like:

```
python build.py path-to-the/kel-website path-to-the/kel-data/ path-to-the/kel-output
```

Following the above setup instructions, `path-to-the/kel-website` would be `.`.
