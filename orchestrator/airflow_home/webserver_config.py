# Disable login entirely: anonymous users get Admin role
from flask_appbuilder.security.manager import AUTH_DB  # required import
AUTH_TYPE = AUTH_DB
AUTH_ROLE_PUBLIC = "Admin"