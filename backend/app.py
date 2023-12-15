import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, User, Deck, Card, Session, History, Card_Status, Deck_Status
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators
import logic 
import time

# API Summary:
# 1. Add Deck (/api/add_deck - POST)
# Parameters: JSON payload containing name (string).
# Output: JSON object with deck_id (int) and deck_name (string).
# Behavior: Creates a new deck with the specified name and returns its ID and name.

# 2. Delete Deck (/api/delete_deck/<int:deck_id> - DELETE)
# Parameters: deck_id (int) in the URL.
# Output: JSON object with success (boolean).
# Behavior: Deletes the deck specified by deck_id and confirms the action with a success flag.

# 3. Add Card (/api/add_card/<int:deck_id> - POST)
# Parameters:
# deck_id (int) in the URL.
# JSON payload containing front (string), back (string), source (string, optional), tags (string, optional).
# Output: JSON object with card_id (int) and deck_id (int).
# Behavior: Adds a new card to the specified deck with the provided details and returns the new card's ID.

# 4. Edit Card (/api/edit_card/<int:card_id> - PUT)
# Parameters:
# card_id (int) in the URL.
# JSON payload containing front (string), back (string), source (string, optional), tags (string, optional).
# Output: JSON object with card_id (int) and deck_id (int).
# Behavior: Updates the specified card's details and returns the card's ID and associated deck ID.

# 5. Review Session (/review/<int:deck_id> - GET, POST)
# Parameters:
# deck_id (int) in the URL.
# For POST: card_id (int) and status (string) in form data.
# Output:
# HTML page for GET.
# Redirects to the same page for POST.
# Behavior:
# GET: Displays the next card for review in the specified deck.
# POST: Submits the review for a card and fetches the next one.

# 6. Submit Review (/submit_review - POST)
# Parameters: Form data with card_id (int), status (string), session_id (int).
# Output: JSON object with success (boolean) and optional error message.
# Behavior: Records the review status for a given card in a session.

# 7. End Session (/end_session/<int:session_id> - POST)
# Parameters: session_id (int) in the URL.
# Output: Redirects to the main screen.
# Behavior: Marks the specified session as ended.

# 8. Import Deck (/import_deck/<int:deck_id> - POST)
# Parameters: deck_id (int) in the URL.
# Output: Redirects to the main screen.
# Behavior: Starts the import process for the specified deck.

# 9. Import Progress (/import_progress/<int:deck_id> - GET)
# Parameters: deck_id (int) in the URL.
# Output: JSON object with importing (boolean) and progress (int).
# Behavior: Provides the current progress of the deck import process.

# 10. All Tags (/tags - GET)
# Parameters: None.
# Output: JSON array of all tags (string) used across cards.
# Behavior: Retrieves a list of all unique tags for autocomplete features.



class Config:
    """Flask configuration from environment variables."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///flashcards.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Add this code after initializing the app and the database to create the default user.
from models import init_db

from datetime import datetime
from wtforms import StringField, TextAreaField, validators

db = init_db(app)

# This is a cheat to make it easier to return all columns from a table
# It really shouldn't be used 
def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

class DeckForm(FlaskForm):
    name = StringField('Deck Name', [validators.InputRequired(message="Deck name is required.")])

class CardForm(FlaskForm):
    front = TextAreaField('Front', [validators.InputRequired(message="Front text is required.")])
    back = TextAreaField('Back', [validators.InputRequired(message="Back text is required.")])
    source = StringField('Source')
    tags = StringField('Tags')

@app.route('/review/<int:deck_id>', methods=['GET', 'POST'])
def review(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    deck_status, session, next_card = logic.review_logic(deck_id, db)

    if request.method == 'POST':
        card_id = request.form['card_id']
        status = request.form['status']
        logic.submit_review_logic(card_id, status, session.id, deck_id, db)
        return redirect(url_for('review', deck_id=deck_id))

    if not next_card:
        return render_template('review.html', deck=deck, card=None, session=session, session_start_time=session.start_time.timestamp())

    return render_template('review.html', deck=deck, card=next_card, session=session, session_start_time=session.start_time.timestamp())

@app.route('/submit_review', methods=['POST'])
def submit_review():
    try:
        card_id = request.form['card_id']
        status = request.form['status']
        session_id = request.form['session_id']
        #deck_id = Card.query.get(card_id).deck_id
        deck_id = db.session.get(Card, card_id).deck_id
        logic.submit_review_logic(card_id, status, session_id, deck_id, db)
        return jsonify(success=True)
    except KeyError as e:
        app.logger.error('KeyError: %s', e)
        return jsonify(success=False, error=str(e))

@app.route('/end_session/<int:session_id>', methods=['POST'])
def end_session(session_id):
    """End the review session."""
    session = Session.query.get_or_404(session_id)
    session.end_time = datetime.now()
    db.session.commit()
    return redirect(url_for('main_screen'))

@app.route('/add_deck', methods=['GET', 'POST'])
def add_deck():
    form = DeckForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name="user").first()  # Assuming user_id is available
        logic.add_deck_logic(form.name.data, user.id, db)
        return redirect(url_for('main_screen'))
    return render_template('add_deck.html', form=form)

@app.route('/api/add_deck', methods=['POST'])
def api_add_deck():
    data = request.get_json()
    user = User.query.filter_by(name="user").first()  # Assuming user_id is available
    deck = logic.add_deck_logic(data['deckName'], user.id, db)
    return jsonify({'deckId': deck.id, 'deckName': deck.name})

@app.route('/delete_deck/<int:deck_id>', methods=['POST'])
def delete_deck(deck_id):
    logic.delete_deck_logic(deck_id, db)
    return redirect(url_for('main_screen'))

@app.route('/api/delete_deck/<int:deck_id>', methods=['DELETE'])
def api_delete_deck(deck_id):
    logic.delete_deck_logic(deck_id, db)
    return jsonify({'success': True})



@app.route('/frontend')
def frontend():
    return render_template('frontend.html')

@app.route('/')
def main_screen():
    """Show the main screen with a list of decks."""
    try:
        deck_stats = []
        decks = Deck.query.all()
        for deck in decks:
            stats = {
                'deck_id': deck.id,
                'deck_name': deck.name,
                'easy': History.query.filter_by(deck_id=deck.id, status='Easy').count(),
                'medium': History.query.filter_by(deck_id=deck.id, status='Medium').count(),
                'hard': History.query.filter_by(deck_id=deck.id, status='Hard').count(),
                'again': History.query.filter_by(deck_id=deck.id, status='Again').count(),
                'no_history': Card.query.filter_by(deck_id=deck.id).filter(~Card.histories.any()).count(),
                'total_cards': History.query.filter_by(deck_id=deck.id).count()
            }
            deck_stats.append(stats)
    except Exception as e:
        return f"An error occurred: {e}", 500
    return render_template('main_screen.html', deck_stats=deck_stats)

@app.route('/add_card/<int:deck_id>', methods=['GET', 'POST'])
def add_card(deck_id):
    form = CardForm()
    if form.validate_on_submit():
        logic.add_card_logic(deck_id, form.front.data, form.back.data, form.source.data, form.tags.data, db)
        return redirect(url_for('edit_deck', deck_id=deck_id))
    return render_template('add_card.html', deck_id=deck_id, form=form)

@app.route('/decks', methods=['GET'])
def api_get_decks():
    decks = Deck.query.all()
    return jsonify([to_dict(deck) for deck in decks])

@app.route('/api/add_card/<int:deck_id>', methods=['POST'])
def api_add_card(deck_id):
    data = request.get_json()
    card = logic.add_card_logic(deck_id, data['front'], data['back'], data.get('source'), data.get('tags'), db)
    return jsonify({'card_id': card.id, 'deck_id': deck_id})

@app.route('/edit_card/<int:card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    form = CardForm(obj=card)
    if form.validate_on_submit():
        logic.edit_card_logic(card_id, form.front.data, form.back.data, form.source.data, form.tags.data, db)
        return redirect(url_for('edit_deck', deck_id=card.deck_id))
    return render_template('edit_card.html', card_id=card_id, form=form)

@app.route('/api/edit_card/<int:card_id>', methods=['PUT'])
def api_edit_card(card_id):
    data = request.get_json()
    card = logic.edit_card_logic(card_id, data['front'], data['back'], data.get('source'), data.get('tags'), db)
    return jsonify({'card_id': card.id, 'deck_id': card.deck_id})

from threading import Thread

@app.route('/import_deck/<int:deck_id>', methods=['POST'])
def import_deck(deck_id):
    """Start the import process for a deck."""
    deck = Deck.query.get_or_404(deck_id)
    deck.importing = True
    deck.progress = 0
    db.session.commit()

    # Start the import in a new thread
    import_thread = Thread(target=do_import, args=(deck_id,))
    import_thread.start()

    return redirect(url_for('main_screen'))

def do_import(deck_id):
    """Perform the deck import."""
    try:
        deck = Deck.query.get(deck_id)
        # Here, implement the actual import logic, updating deck.progress as needed
        # For now, we'll simulate a simple import process
        for i in range(1, 101):
            deck.progress = i
            db.session.commit()
            time.sleep(1)  # Simulate time-consuming task

        deck.importing = False
        db.session.commit()
    except Exception as e:
        # Handle exceptions and set importing to False in case of failure
        deck.importing = False
        db.session.commit()
        app.logger.error(f"Import failed for deck {deck_id}: {e}")

@app.route('/import_progress/<int:deck_id>')
def import_progress(deck_id):
    """Get the import progress for a deck."""
    deck = Deck.query.get_or_404(deck_id)
    return jsonify({
        'importing': deck.importing,
        'progress': deck.progress
    })

def import_deck(deck_id):
    """Start the import process for a deck."""
    deck = Deck.query.get_or_404(deck_id)
    deck.importing = True
    deck.progress = 0
    db.session.commit()

    # Start the import in a new thread
    import_thread = Thread(target=do_import, args=(deck_id,))
    import_thread.start()

    return redirect(url_for('main_screen'))

@app.route('/tags')
def all_tags():
    """Retrieve all tags for autocomplete."""
    all_tags_set = set()
    cards = Card.query.with_entities(Card.tags).all()
    for card in cards:
        if card.tags:
            all_tags_set.update(card.tags.split(','))

    return jsonify(list(all_tags_set))

if __name__ == '__main__':
    app.run(debug=True)
