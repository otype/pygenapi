REQUIREMENTS
----------------------------------------------------
Following libraries are required to run PyGenAPI:

- riak
- tornado
- ez_setup
- riak
- pycurl
- requests


You can use the 'requirements.txt' to install the 
dependencies:

    $ pip install -r requirements.txt


RUN PYGENAPI
----------------------------------------------------
If you're using virtualenv (http://www.virtualenv.org/en/latest/index.html)
create a virtual environment first:

    $ mkvirtualenv pygenapi

Then install the dependencies:

    $ pip install -r requirements.txt

Finally, run PyGenAPI:

    $ ./start_genapi.sh <options>

For help:

    $ ./start_genapi.sh --help
