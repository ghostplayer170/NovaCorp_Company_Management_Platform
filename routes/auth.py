from db import get_users_connection, hash_password, check_password, needs_rehash, is_strong_password
from flask import request, redirect, render_template, session, flash
from server import app, is_safe_url

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/dashboard')
    next_url = request.args.get('next', '/dashboard')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_users_connection()
        user = conn.execute("SELECT *, (julianday('now') - julianday(password_updated_at)) > 90 as is_expired FROM users WHERE username = ?", (username,)).fetchone()
        
        if user and check_password(user['password'], password):
            # Migration to bcrypt if needed
            if needs_rehash(user['password']):
                new_hash = hash_password(password)
                conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user['id']))
                conn.commit()
            
            conn.close()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['company_id'] = user['company_id']
            session.permanent = True
            
            if user['is_expired']:
                session['password_expired'] = True
                return redirect('/change_password')
            
            session['password_expired'] = False
            
            # Validate next_url to prevent Open Redirect
            if not next_url or not is_safe_url(next_url):
                next_url = '/dashboard'
                
            return redirect(next_url)
        else:
            conn.close()
            flash("Invalid username or password", "danger")
            return render_template('auth/login.html', next_url=next_url)
    return render_template('auth/login.html', next_url=next_url)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/login')

@app.before_request
def check_password_change():
    allowed_endpoints = ['login', 'logout', 'change_password', 'static']
    if request.endpoint not in allowed_endpoints and session.get('password_expired'):
        flash("Your password has expired. Please change it to continue.", "warning")
        return redirect('/change_password')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect('/login')
        
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        conn = get_users_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
        
        if not check_password(user['password'], current_password):
            flash("Current password is incorrect.", "danger")
        elif new_password != confirm_password:
            flash("New passwords do not match.", "danger")
        elif current_password == new_password:
            flash("New password must be different from the current one.", "danger")
        else:
            is_strong, msg = is_strong_password(new_password)
            if not is_strong:
                flash(msg, "danger")
            else:
                conn.execute("UPDATE users SET password = ?, password_updated_at = CURRENT_TIMESTAMP WHERE username = ?", 
                             (hash_password(new_password), session['username']))
                conn.commit()
                session['password_expired'] = False
                flash("Password updated successfully.", "success")
                conn.close()
                return redirect('/dashboard')
        conn.close()
        
    return render_template('auth/change_password.html')
