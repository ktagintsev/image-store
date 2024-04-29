from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from datetime import datetime, timezone
import sqlalchemy as sa

# from app import app
from app import db
from app.models.user import User
from app.models.reward import Reward
from app.users import bp

from flask_login import current_user, login_user, logout_user, login_required
from app.users.forms import EditProfileForm


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()



@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    image_count = user.get_image_count(user.id)
    purchase_count = user.get_purchase_count(user.id)


    if user.id != current_user.id:
        flash('You are not allowed to access that location.')
        return redirect(url_for('main.index'))

    recent_rewards = Reward.query.filter_by(user_id=user.id).order_by(Reward.timestamp.desc()).limit(20).all()
    
    return render_template('users/user.html', user = user, image_count = image_count, purchase_count = purchase_count, recent_rewards = recent_rewards)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('users.user',username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('users/edit_profile.html', title='Edit Profile',
                           form=form)

