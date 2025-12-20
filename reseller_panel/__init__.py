from flask import Blueprint

# Initialize Blueprint
# url_prefix will be set when registering in webapp.py, but we can default to /reseller
reseller_bp = Blueprint(
    'reseller', 
    __name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/reseller/static'
)

from . import routes
