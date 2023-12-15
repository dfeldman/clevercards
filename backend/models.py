from flask_sqlalchemy import SQLAlchemy
import datetime 
from datetime import timedelta

db = SQLAlchemy()

class User(db.Model):
    """Represents a user of the flashcard app."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    decks = db.relationship('Deck', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

class Deck(db.Model):
    """Represents a deck of flashcards."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cards = db.relationship('Card', backref='deck', lazy=True, cascade="all,delete")
    deck_status = db.relationship('Deck_Status', backref='deck', uselist=False)
    importing = db.Column(db.Boolean, default=False)
    progress = db.Column(db.Integer, default=0)
    def __repr__(self):
        return f'<Deck {self.name}>'

class Card(db.Model):
    """Represents a flashcard with a front and a back."""
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.Text(length=1000), nullable=False)
    back = db.Column(db.Text(length=1000), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    histories = db.relationship('History', backref='card', lazy=True)
    card_status = db.relationship('Card_Status', backref='card', uselist=False)
    source = db.Column(db.Text(length=1000), nullable=True)
    tags = db.Column(db.Text(length=1000), nullable=True)
    def __repr__(self):
        return f'<Card {self.front}>'

class Session(db.Model):
    """Represents a study session."""
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    histories = db.relationship('History', backref='session', lazy=True)

    def __repr__(self):
        return f'<Session {self.start_time}>'

class History(db.Model):
    """Represents the history of a card review during a session."""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<History {self.status}>'
    
class Deck_Status(db.Model):
    """Represents the status of a deck for a user."""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), primary_key=True)
    step = db.Column(db.Integer, default=0)
    progress_score = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Interval, default=timedelta(0))

class Card_Status(db.Model):
    """Represents the status of a card."""
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    status = db.Column(db.String(50))
    target_step = db.Column(db.Integer)

def increase_step(user_id, deck_id):
    deck_status = Deck_Status.query.get((user_id, deck_id))
    deck_status.step += 1
    db.session.commit()

def reset_step(user_id, deck_id):
    deck_status = Deck_Status.query.get((user_id, deck_id))
    deck_status.step = 0
    db.session.commit()

def update_card_status(card_id, new_status, target_step):
    card_status = Card_Status.query.get(card_id)
    if not card_status:
        card_status = Card_Status(card_id=card_id)
        db.session.add(card_status)
    card_status.status = new_status
    card_status.target_step = target_step
    db.session.commit()

# Add this function at the end of the models.py file
def init_db(app):
    with app.app_context():
        db.create_all()
        # Create a default user if not exists
        if not User.query.filter_by(name="user").first():
            user = User(name="user")
            db.session.add(user)
            db.session.commit()
    return db
