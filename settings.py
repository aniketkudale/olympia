"""This is the standard development settings file.

If you need to overload settings, please do so in a local_settings.py file (it
won't be tracked in git).

"""
import os

from lib.settings_base import *  # noqa

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = False

# These apps are great during development.
INSTALLED_APPS += (
    'django_extensions',
    'landfill',
)

# Using locmem deadlocks in certain scenarios. This should all be fixed,
# hopefully, in Django1.7. At that point, we may try again, and remove this to
# not require memcache installation for newcomers.
# A failing scenario is:
# 1/ log in
# 2/ click on "Submit a new addon"
# 3/ click on "I accept this Agreement" => request never ends
#
# If this is changed back to locmem, make sure to use it from "caching" (by
# default in Django for locmem, a timeout of "0" means "don't cache it", while
# on other backends it means "cache forever"):
#      'BACKEND': 'caching.backends.locmem.LocMemCache'
CACHES = {
    'default': {
        'BACKEND': 'caching.backends.memcached.MemcachedCache',
        'LOCATION': os.environ.get('MEMCACHE_LOCATION', 'localhost:11211'),
    }
}

HAS_SYSLOG = False  # syslog is used if HAS_SYSLOG and NOT DEBUG.

# If you're not running on SSL you'll want this to be False.
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = None

CELERY_ALWAYS_EAGER = False
CELERY_ROUTES = {}

# If you want to allow self-reviews for add-ons/apps, then enable this.
# In production we do not want to allow this.
ALLOW_SELF_REVIEWS = True

# Assuming you did `npm install` (and not `-g`) like you were supposed to, this
# will be the path to the `stylus` and `lessc` executables.
STYLUS_BIN = os.getenv('STYLUS_BIN', path('node_modules/stylus/bin/stylus'))
LESS_BIN = os.getenv('LESS_BIN', path('node_modules/less/bin/lessc'))
CLEANCSS_BIN = os.getenv(
    'CLEANCSS_BIN',
    path('node_modules/clean-css/bin/cleancss'))
UGLIFY_BIN = os.getenv(
    'UGLIFY_BIN',
    path('node_modules/uglify-js/bin/uglifyjs'))
VALIDATOR_BIN = os.getenv(
    'VALIDATOR_BIN',
    path('node_modules/addons-validator/bin/addons-validator'))

# Locally we typically don't run more than 1 elasticsearch node. So we set
# replicas to zero.
ES_DEFAULT_NUM_REPLICAS = 0

SITE_URL = os.environ.get('OLYMPIA_SITE_URL') or 'http://localhost:8000'
SERVICES_DOMAIN = 'localhost:8000'
SERVICES_URL = 'http://%s' % SERVICES_DOMAIN

VALIDATE_ADDONS = True

ADDON_COLLECTOR_ID = 1

# Default AMO user id to use for tasks (from users.json fixture in zadmin).
TASK_USER_ID = 10968

# Set to True if we're allowed to use X-SENDFILE.
XSENDFILE = False


AES_KEYS = {
    'api_key:secret': os.path.join(ROOT, 'apps', 'api', 'tests', 'assets',
                                   'test-api-key.txt'),
}

# FxA config for local development only.
FXA_CONFIG = {
    'client_id': 'cd5a21fafacc4744',
    'client_secret':
        '4db6f78940c6653d5b0d2adced8caf6c6fd8fd4f2a3a448da927a54daba7d401',
    'content_host': 'https://stable.dev.lcip.org',
    'oauth_host': 'https://oauth-stable.dev.lcip.org/v1',
    'profile_host': 'https://stable.dev.lcip.org/profile/v1',
    'redirect_url': 'http://olympia.dev/api/v3/accounts/authorize/',
    'scope': 'profile',
}

# CSP report endpoint which returns a 204 from addons-nginx in local dev.
CSP_REPORT_ONLY = False
CSP_REPORT_URI = '/csp-report'

# Allow GA over http + www subdomain in local development.
HTTP_GA_SRC = 'http://www.google-analytics.com'
CSP_FRAME_SRC += ('https://www.sandbox.paypal.com',)
CSP_IMG_SRC += (HTTP_GA_SRC,)
CSP_SCRIPT_SRC += (HTTP_GA_SRC,)

# If you have settings you want to overload, put them in a local_settings.py.
try:
    from local_settings import *  # noqa
except ImportError:
    pass
