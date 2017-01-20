# -*- coding: utf-8 -*-

from __future__ import absolute_import

import redis
from flask import _request_ctx_stack

try:
    from flask import _app_ctx_stack
except ImportError:
    _app_ctx_stack = None

app_stack = _app_ctx_stack or _request_ctx_stack


class _RedisState(object):
    def __init__(self, redis):
        self.redis = redis
        self.connectors = {}


class Redis(object):
    def __init__(self, app=None, strict=True, config_prefix='REDIS', **kwargs):
        self.config_prefix = config_prefix
        self.redis_klass = redis.StrictRedis if strict else redis.Redis
        self.redis_klass_kwargs = kwargs
        self.config_key = '{0}_URL'.format(self.config_prefix)
        if app:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app, **kwargs):
        app.config.setdefault(self.config_key, 'redis://localhost:6379/0')

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        self.redis_klass_kwargs.update(kwargs)
        app.extensions[self.config_prefix] = _RedisState(self)

    def get_app(self, reference_app=None):
        if reference_app is not None:
            return reference_app
        if self.app is not None:
            return self.app
        ctx = app_stack.top
        if ctx is not None:
            return ctx.app
        raise RuntimeError('application not registered on db '
                           'instance and no application bound '
                           'to current context')

    @property
    def redis_client(self):
        app = self.get_app()
        connectors = app.extensions[self.config_prefix].connectors
        client = connectors.get('redis_client')
        if not client:
            client = self.redis_klass.from_url(app.config[self.config_key], **self.redis_klass_kwargs)
            connectors['redis_client'] = client
        return client

    def __getattr__(self, name):
        return getattr(self.redis_client, name)

    def __getitem__(self, name):
        return self.redis_client[name]

    def __setitem__(self, name, value):
        self.redis_client[name] = value

    def __delitem__(self, name):
        del self.redis_client[name]

    def __repr__(self):
        return "<%s connector=%s>" % (self.__class__.__name__, str(self.redis_client))
