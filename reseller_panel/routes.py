from flask import render_template, request, jsonify, flash, redirect, url_for
from . import reseller_bp
from .models import ResellerManager
from .utils import admin_required, format_currency
import logging

logger = logging.getLogger(__name__)

@reseller_bp.route('/dashboard')
@admin_required
def dashboard():
    """Reseller System Dashboard."""
    from webapp import get_db
    db = get_db()
    manager = ResellerManager(db)
    
    stats = manager.get_total_stats()
    recent_resellers = manager.get_all_resellers()[:5]
    
    return render_template(
        'reseller/dashboard.html',
        stats=stats,
        recent_resellers=recent_resellers,
        format_currency=format_currency
    )

@reseller_bp.route('/resellers')
@admin_required
def resellers_list():
    """List all resellers."""
    from webapp import get_db
    db = get_db()
    manager = ResellerManager(db)
    resellers = manager.get_all_resellers()
    return render_template(
        'reseller/resellers.html',
        resellers=resellers,
        format_currency=format_currency
    )

@reseller_bp.route('/resellers/add', methods=['POST'])
@admin_required
def add_reseller():
    """Add or update a reseller."""
    try:
        user_id = request.form.get('user_id')
        level = request.form.get('level', 'standard')
        commission = float(request.form.get('commission', 10.0))
        discount = float(request.form.get('discount', 0.0))
        
        if not user_id:
            flash('لطفاً یک کاربر انتخاب کنید.', 'error')
            return redirect(url_for('reseller.resellers_list'))
        
        from webapp import get_db
        db = get_db()
        manager = ResellerManager(db)
        
        if manager.create_or_update_reseller(user_id, level, commission, discount):
            flash('نماینده با موفقیت ذخیره شد.', 'success')
        else:
            flash('خطا در ذخیره نماینده.', 'error')
            
    except Exception as e:
        logger.error(f"Error adding reseller: {e}")
        flash(f'خطا: {str(e)}', 'error')
        
    return redirect(url_for('reseller.resellers_list'))

@reseller_bp.route('/resellers/delete/<int:user_id>')
@admin_required
def delete_reseller(user_id):
    """Delete a reseller."""
    try:
        from webapp import get_db
        db = get_db()
        manager = ResellerManager(db)
        
        if manager.delete_reseller(user_id):
            flash('نماینده با موفقیت حذف شد.', 'success')
        else:
            flash('خطا در حذف نماینده.', 'error')
    except Exception as e:
        logger.error(f"Error deleting reseller: {e}")
        flash(f'خطا: {str(e)}', 'error')
        
    return redirect(url_for('reseller.resellers_list'))

@reseller_bp.route('/settings')
@admin_required
def settings():
    """Reseller system settings."""
    return render_template('reseller/settings.html')

@reseller_bp.route('/api/chart-data')
@admin_required
def api_chart_data():
    """API for dashboard charts."""
    from webapp import get_db
    db = get_db()
    manager = ResellerManager(db)
    data = manager.get_chart_data()
    return jsonify(data)

@reseller_bp.route('/api/search-user')
@admin_required
def search_user():
    """Search users by telegram_id or username."""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'users': []})
    
    try:
        from webapp import get_db
        db = get_db()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Search by telegram_id (exact or partial) or username
            search_query = f"%{query}%"
            cursor.execute('''
                SELECT id, telegram_id, username, first_name, last_name, balance
                FROM users
                WHERE telegram_id LIKE %s 
                   OR username LIKE %s 
                   OR first_name LIKE %s
                   OR CAST(telegram_id AS CHAR) = %s
                ORDER BY created_at DESC
                LIMIT 10
            ''', (search_query, search_query, search_query, query))
            
            users = cursor.fetchall()
            
            # Convert to serializable format
            result = []
            for user in users:
                result.append({
                    'id': user['id'],
                    'telegram_id': str(user['telegram_id']),
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'balance': user['balance']
                })
            
            return jsonify({'users': result})
            
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        return jsonify({'users': [], 'error': str(e)})
