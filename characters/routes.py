from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, Character, Universe
import os
from werkzeug.utils import secure_filename
from config import Config
from forms import CharacterForm  # ← Добавь эту строку

import requests
import json

# Blueprint for character-related routes
characters_bp = Blueprint('characters', __name__)

# Dashboard view showing user's characters
@characters_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    # Get all characters belonging to the logged-in user
    characters = Character.query.filter_by(user_id=session['user_id']).all()
    universes = Universe.query.all()  # For filter dropdown
    return render_template('dashboard.html', characters=characters, universes=universes)

# Search characters
@characters_bp.route('/search', methods=['GET', 'POST'])
def search_characters():
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    search_query = request.form.get('search_query', '') if request.method == 'POST' else request.args.get('search_query', '')
    characters = Character.query.filter(
        Character.user_id == session['user_id'],
        Character.name.ilike(f'%{search_query}%')
    ).all()
    universes = Universe.query.all()
    return render_template('dashboard.html', characters=characters, universes=universes, search_query=search_query)

# Filter characters by universe
@characters_bp.route('/filter_by_universe', methods=['GET'])
def filter_by_universe():
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    universe_id = request.args.get('universe_id', type=int)
    if universe_id:
        characters = Character.query.filter_by(user_id=session['user_id'], universe_id=universe_id).all()
        selected_universe = Universe.query.get_or_404(universe_id)
    else:
        characters = Character.query.filter_by(user_id=session['user_id']).all()
        selected_universe = None
    universes = Universe.query.all()
    return render_template('dashboard.html', characters=characters, universes=universes, selected_universe=selected_universe)

# View character details
@characters_bp.route('/character/<int:char_id>')
def view_character(char_id):
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    character = Character.query.get_or_404(char_id)
    if character.user_id != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('characters.dashboard'))

    return render_template('character_detail.html', character=character)

# Create a new character
@characters_bp.route('/create_character', methods=['GET', 'POST'])
def create_character():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    form = CharacterForm()
    # Populate universe choices dynamically
    form.universe.choices = [(u.id, u.name) for u in Universe.query.all()]

    if form.validate_on_submit():
        filename = None
        # Save uploaded image if provided
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(Config.UPLOAD_FOLDER, filename))

        # Create and save new character
        new_character = Character(
            name=form.name.data,
            age=form.age.data,
            appearance=form.appearance.data,
            personality=form.personality.data,
            backstory=form.backstory.data,
            image_filename=filename,
            universe_id=form.universe.data,
            user_id=session['user_id']
        )
        db.session.add(new_character)
        db.session.commit()
        flash('Character created successfully!', 'success')
        return redirect(url_for('characters.dashboard'))

    return render_template('create_character.html', form=form)

# Edit an existing character
@characters_bp.route('/edit_character/<int:char_id>', methods=['GET', 'POST'])
def edit_character(char_id):
    character = Character.query.get_or_404(char_id)

    # Ensure the character belongs to the current user
    if character.user_id != session.get('user_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('characters.dashboard'))

    form = CharacterForm(obj=character)
    form.universe.choices = [(u.id, u.name) for u in Universe.query.all()]

    if form.validate_on_submit():
        # Update character fields
        character.name = form.name.data
        character.age = form.age.data
        character.appearance = form.appearance.data
        character.personality = form.personality.data
        character.backstory = form.backstory.data
        character.universe_id = form.universe.data

        # Handle new image upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            character.image_filename = filename

        db.session.commit()
        flash('Character updated!', 'success')
        return redirect(url_for('characters.dashboard'))

    return render_template('edit_character.html', form=form)

# Delete a character
@characters_bp.route('/delete_character/<int:char_id>', methods=['POST'])
def delete_character(char_id):
    character = Character.query.get_or_404(char_id)

    # Check ownership before deleting
    if character.user_id != session.get('user_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('characters.dashboard'))

    db.session.delete(character)
    db.session.commit()
    flash('Character deleted!', 'info')
    return redirect(url_for('characters.dashboard'))