import logging
import os
import platform
from fle_utils.settingshelper import import_installed_app_settings


##############################
# Basic setup
##############################

try:
    from local_settings import *
    import local_settings
except ImportError:
    local_settings = object()


# Used everywhere, so ... set it up top.
DEBUG          = getattr(local_settings, "DEBUG", False)

CENTRAL_SERVER = True  # Hopefully will be removed soon.

##############################
# Basic setup of logging
##############################

# Set logging level based on the value of DEBUG (evaluates to 0 if False, 1 if True)
LOGGING_LEVEL = getattr(local_settings, "LOGGING_LEVEL", logging.DEBUG if DEBUG else logging.INFO)
LOG = getattr(local_settings, "LOG", logging.getLogger("kalite"))
TEMPLATE_DEBUG = getattr(local_settings, "TEMPLATE_DEBUG", DEBUG)

logging.basicConfig()
LOG.setLevel(LOGGING_LEVEL)
logging.getLogger("requests").setLevel(logging.WARNING)  # shut up requests!

ADMINS = (('FLE Errors', 'errors@learningequality.org'),)
SERVER_EMAIL = 'kalite@learningequality.org'

##############################
# Basic Django settings
##############################

# Not really a Django setting, but we treat it like one--it's eeeeverywhere.
PROJECT_PATH = os.path.realpath(getattr(local_settings, "PROJECT_PATH", os.path.dirname(os.path.realpath(__file__)))) + "/"
ROOT_DATA_PATH = os.path.realpath(getattr(local_settings, "ROOT_DATA_PATH", os.path.join(PROJECT_PATH, "..", "data"))) + "/"
KALITE_PATH    = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'ka-lite-submodule') + "/"

LOCALE_PATHS   = getattr(local_settings, "LOCALE_PATHS", (PROJECT_PATH + "/../locale",))
LOCALE_PATHS   = tuple([os.path.realpath(lp) + "/" for lp in LOCALE_PATHS])

DATABASES      = getattr(local_settings, "DATABASES", {
    "default": {
        "ENGINE": getattr(local_settings, "DATABASE_TYPE", "django.db.backends.sqlite3"),
        "NAME"  : getattr(local_settings, "DATABASE_PATH", os.path.join(PROJECT_PATH, "database", "data.sqlite")),
        "OPTIONS": {
            "timeout": 60,
        },
    }
})

ALLOWED_HOSTS = getattr(local_settings, "ALLOWED_HOSTS", ['*'])
INTERNAL_IPS   = getattr(local_settings, "INTERNAL_IPS", ("127.0.0.1",))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE      = getattr(local_settings, "TIME_ZONE", None)
#USE_TZ         = True  # needed for timezone-aware datetimes (particularly in updates code)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE  = getattr(local_settings, "LANGUAGE_CODE", "en")

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N       = getattr(local_settings, "USE_I18N", True)

# If you set this to True, Django will format dates, numbers and
# calendars according to the current locale
USE_L10N       = getattr(local_settings, "USE_L10N", False)

MEDIA_URL      = getattr(local_settings, "MEDIA_URL", "/media/")
MEDIA_ROOT     = os.path.realpath(getattr(local_settings, "MEDIA_ROOT", PROJECT_PATH + "/media/")) + "/"
STATIC_URL     = getattr(local_settings, "STATIC_URL", "/static/")
STATIC_ROOT    = os.path.realpath(getattr(local_settings, "STATIC_ROOT", PROJECT_PATH + "/static/")) + "/"

 # Make this unique, and don't share it with anybody.
SECRET_KEY     = getattr(local_settings, "SECRET_KEY", "8qq-!fa$92i=s1gjjitd&%s@4%ka9lj+=@n7a&fzjpwu%3kd#u")

AUTH_PROFILE_MODULE     = "centralserver.central.UserProfile"
CSRF_COOKIE_NAME        = "csrftoken_central"
LANGUAGE_COOKIE_NAME    = "django_language_central"
SESSION_COOKIE_NAME     = "sessionid_central"

ROOT_URLCONF = "centralserver.central.urls"

INSTALLED_APPS = (
    "django.contrib.admin",  # this and the following are needed to enable django admin.
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django_extensions", # needed for clean_pyc (testing)
    "debug_toolbar",
    "centralserver.central",
    "centralserver.testing",
    "fle_utils.handlebars",
) + getattr(local_settings, 'INSTALLED_APPS', tuple())

MIDDLEWARE_CLASSES = (
    "centralserver.middleware.DummySessionForAPIUrls",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",  # needed for django admin
) + getattr(local_settings, 'MIDDLEWARE_CLASSES', tuple())

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.messages.context_processors.messages",  # needed for django admin
) + getattr(local_settings, 'TEMPLATE_CONTEXT_PROCESSORS', tuple())

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, '..', 'static-libraries'),
    os.path.join(PROJECT_PATH, '..', 'ka-lite-submodule', 'static-libraries'),
)  # libraries common to all apps

DEFAULT_ENCODING = 'utf-8'


########################
# Storage and caching
########################

# Sessions use the default cache, and we want a local memory cache for that.
CACHES = {
    "default": {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Separate session caching from file caching.
SESSION_ENGINE = getattr(local_settings, "SESSION_ENGINE", 'django.contrib.sessions.backends.cache' + (''))

# Use our custom message storage to avoid adding duplicate messages
MESSAGE_STORAGE = 'fle_utils.django_utils.NoDuplicateMessagesSessionStorage'



########################
# After all settings, but before config packages,
#   import settings from other apps.
#
# This allows app-specific settings to be localized and augment
#   the settings here, while also allowing
#   config packages to override settings.
########################


#CONTENT_ROOT   = None  # needed for shared functions that are distributed-only
#CONTENT_URL    = None

CACHE_TIME = 0
CACHE_NAME = None
CENTRAL_SERVER_HOST = ""

import_installed_app_settings(INSTALLED_APPS, globals())

TEST_RUNNER = CENTRALSERVER_TEST_RUNNER

RUNNING_IN_TRAVIS = bool(os.environ.get("TRAVIS"))

# LOG.debug("======== MIDDLEWARE ========")
# LOG.debug("\n".join(MIDDLEWARE_CLASSES))
# LOG.debug("====== INSTALLED_APPS ======")
# LOG.debug("\n".join(INSTALLED_APPS))
# LOG.debug("============================")

########################
# Now that we've imported the settings from all other installed apps,
#   override their settings as necessary to get desired central server config.
########################

# Don't want to have a limited number of SyncSession records on the central server (save them all!)
SYNC_SESSIONS_MAX_RECORDS = getattr(local_settings, "SYNC_SESSIONS_MAX_RECORDS", None)

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'

CONFIG_PACKAGE = []
AUTH_PROFILE_MODULE = "central.UserProfile"

# Tastypie stuff
TASTYPIE_DEFAULT_FORMATS = ['json']
API_LIMIT_PER_PAGE = 0
