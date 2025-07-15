# [doc](../README.md) > Installation

This system consists of two elements: station (which is intended to run on a Raspberry Pi with an SDR dongle, but can
be run on any Linux box) and a server (which is intended to be run in a place with good uplink connectivity). If
you are interested in running your own station, you most likely want to deploy just the station and use existing
server. Please contact someone from the Svarog team and we'll hook you up.

## Server installation

Server installation is a manual process. It is assumed that you already have running apache server.
Here are the steps needed to get it up and running.

1. **Get the latest code**

```
git clone https://github.com/gut-space/svarog-server
```

2. **Install PostgreSQL**:

```
apt install postgresql postgresql-client
su - postgres
psql
CREATE DATABASE svarog;
CREATE USER svarog WITH PASSWORD 'secret'; -- make sure to use an actual password here
GRANT ALL PRIVILEGES ON DATABASE svarog TO svarog;
```

If upgrading from earlier Postgres, the following might be helpful:

```sql
grant all ON ALL TABLES IN SCHEMA public to svarog;
grant all ON ALL SEQUENCES IN SCHEMA public to svarog;
grant all ON ALL ROUTINES IN SCHEMA public to svarog;
```

Make sure to either run `setup.py` or run DB schema migration manually: `python3 migrate_db.py`.

3. **Install Flask dependencies**

```
cd svarog-server/server
python3 -m venv venv
source venv/bin/activate
python setup.py install
```

Sometimes it's necessary to explicitly say which python version to use: `python3 -m virtualenv --python=python3 venv`

This step will install necessary dependencies. It is a good practice to install them in virtual environment. If you don't have virtualenv
installed, you can add it with `sudo apt install python-virtualenv`
or similar command for your system. Alternatively, you may use venv.
However, make sure the virtual environment is created in venv directory.

You can start flask manually to check if it's working. This is not needed once you have apache integration complete.

```
cd server
./svarog-web.py
```

4. **Set up your HTTP server**

Svarog has been run successfully with both Apache and Nginx. The very subjective experience of
one of Svarog authors is that Apache's WSGI configuration is much more fragile, but is somewhat
simpler due to fewer components. On the other hand, using Nginx requires additional application
server (Unit), but it is much more robust and flexible. Other stacks are most likely possible,
but were not tried.

Depending on your choice, please follow either 4A or 4B sections.

4A. **Apache configuration**

The general goal is to have an apache2 running with WSGI scripting capability that runs Flask. See an [example
apache2 configuation](apache2/svarog.conf). You may want to tweak the paths and TLS configuration to use LetsEncrypt
or another certificate of your choice. Make sure the paths are actually pointing to the right directory.
There is an example WSGI script in [svarog.wsgi](apache2/svarog.wsgi). It requires some tuning specific to your deloyment.

4B. **NGINX + UNIT Configuration**

An alternative to apache is to run Nginx with Unit application server. Example configuration
for nginx is available [here](nginx/nginx). This file should in general be copied to
`/etc/nginx/sites-available/svarog` and then linked to `/etc/nginx/sites-enabled/svarog`.
Make sure you tweak it to your specific deployment.

This deployment requires Unit app server to run and be configured with the [unit config](nginx/unit.json)
file. The configuration can be uploaded using command similar to this:

```curl -X PUT --data-binary @nginx/unit.json --unix-socket /var/run/control.unit.sock http://localhost/config```

Please consult with [Unit docs](https://unit.nginx.org/configuration/) for
details.

You can check Unit's configuration using:

```curl --unix-socket /var/run/control.unit.sock http://localhost/config/```


4C. **NGINX + Gunicorn**

Gunicorn is a lightweight application server. You can install it:

```
cd server
source venv/bin/activate
pip install gunicorn
```

And then serve the service: `gunicorn app:app`. Plenty of extra options available for
logging (-access-logfile, --error-logfile), binding to specific address or port (--bind 192.168.1.1:1234),
serving over HTTPS/TLS (--keyfile, --certfile) and more.

The gunicorn process can be run from systemd. An example systemd file is available in doc/gunicorn.

5. **Grant sudo privileges**

Also, you should update the /etc/sudoers file to allow ordinary user (svarog) to restart (apache) or (nginx and unit) server.
This will be used by the update script that's being run every day. You should use `visudo` command to add the following line:

```
%svarog ALL= NOPASSWD: /bin/systemctl restart apache2
```

or

```
%svarog ALL= NOPASSWD: /bin/systemctl restart nginx
%svarog ALL= NOPASSWD: /bin/systemctl restart unit
```

Alternatively, you can allow restarting all services:
```
%svarog ALL= NOPASSWD: /bin/systemctl
```

This is more convenient, but may be a bit risky from the security perspective.
