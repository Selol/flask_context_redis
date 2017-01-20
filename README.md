# flask_context_redis
A Flask extension for redis, support app context

## Why use flask_context_redis

If using flask_redis, you may face issus like this
Imaging you are using app factory, you may write code like this

```python
from flask import Flask
from config import config
from flask_redis import Redis
from yourmodels import User # use flask_sqlalchemy
...

redis = Redis()

def create_app(config_name):
    app = Flask(__name__)
    ...
    redis.init_app(app)
    return app
```
You may have multipe app, just like me

```python
cn_app = create_app('CN')
en_app = create_app('EN')
```

You may have crontab tasks, to update data from redis to mysql.
You want to write them in one script, it's easier to maintain than separate them.

```python
with cn_app.app_context():
    User.update()
with en_app.app_context():
    User.update()
```

And you will find, both cn_app and en_app will use redis connection in config 'EN'
Due to flask_redis dose not support app_context(although flask_sqlalchemy does), it will use the last config.

So just change this line

```python
from flask_redis import Redis
```
to
```python
from flask_context_redis import Redis
```

##Configuration

Your configuration should be declared within your Flask config. Set the URL of your database like this:

```python
REDIS_URL = "redis://redis.domain:6379/0"
# Default Value
# REDIS_URL = 'redis://localhost:6379/0' 
```

