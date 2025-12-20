import logging
from functools import wraps
from flask import session, redirect, url_for, flash, request, render_template

logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator to require admin login for reseller panel access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and is admin
        # This relies on the session structure from the main webapp
        if 'user_id' not in session:
            return redirect(url_for('index', next=request.path))
        
        # Verify admin status from DB to be safe
        try:
            from webapp import get_db
            db = get_db()
            user_id = session['user_id']
            # session['user_id'] is the Telegram ID, so we use get_user() which queries by telegram_id
            user = db.get_user(user_id)
            
            logger.info(f"Reseller Admin Check: UserID={user_id}, User={user.get('username') if user else 'None'}, IsAdmin={user.get('is_admin') if user else 'None'}")
            
            if not user or not user.get('is_admin'):
                logger.warning(f"Access denied for user {user_id} to reseller panel")
                # If logged in but not admin, return 403 instead of redirecting to index (which redirects to dashboard)
                return render_template('reseller/403.html'), 403
                
        except Exception as e:
            logger.error(f"Auth check error: {e}")
            return render_template('reseller/403.html'), 403
            
        return f(*args, **kwargs)
    return decorated_function

def format_currency(value):
    """Format currency with commas."""
    try:
        return f"{int(value):,}"
    except:
        return "0"
