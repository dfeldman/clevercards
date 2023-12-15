from models import db, User, Deck, Card, Session, History, Card_Status, Deck_Status

from datetime import datetime
from threading import Thread

# Business logic functions
def add_deck_logic(deck_name, user_id, db):
    new_deck = Deck(name=deck_name, user_id=user_id)
    db.session.add(new_deck)
    db.session.flush()
    new_deck_status = Deck_Status(user_id=user_id, deck_id=new_deck.id)
    db.session.add(new_deck_status)
    db.session.commit()
    return new_deck

def delete_deck_logic(deck_id, db):
    deck = Deck.query.get_or_404(deck_id)
    db.session.delete(deck)
    db.session.commit()

def add_card_logic(deck_id, front, back, source, tags, db):
    new_card = Card(front=front, back=back, deck_id=deck_id, source=source, tags=tags)
    db.session.add(new_card)
    db.session.flush()
    new_card_status = Card_Status(card_id=new_card.id, status="", target_step=0)
    db.session.add(new_card_status)
    db.session.commit()
    return new_card

def edit_card_logic(card_id, front, back, source, tags, db):
    card = Card.query.get_or_404(card_id)
    card.front = front
    card.back = back
    card.source = source
    card.tags = tags
    db.session.commit()
    return card

# API logic functions for additional endpoints
def get_deck_logic(deck_id, db):
    deck = Deck.query.get_or_404(deck_id)
    return deck

def review_logic(deck_id, db):
    deck = Deck.query.get_or_404(deck_id)
    deck_status = Deck_Status.query.filter_by(deck_id=deck_id).first()
    if not deck_status:
        deck_status = Deck_Status(user_id=deck.user_id, deck_id=deck_id)
        db.session.add(deck_status)
        db.session.commit()

    session = Session.query.filter_by(end_time=None).first()
    if not session:
        session = Session(start_time=datetime. now())
        db.session.add(session)
        db.session.commit()

    next_card = (Card.query
                 .join(Card_Status, Card.id == Card_Status.card_id)
                 .filter(Card.deck_id == deck_id, Card.enabled == True, Card.deleted == False)
                 .filter(Card_Status.target_step <= deck_status.step)
                 .order_by(Card.id)
                 .first())

    if not next_card:
        session.end_time = datetime.now()
        db.session.commit()

    return deck_status, session, next_card

def submit_review_logic(card_id, status, session_id, deck_id, db):
    history = History(session_id=session_id, deck_id=deck_id, card_id=card_id, status=status)
    db.session.add(history)
    db.session.commit()

def import_deck_logic(deck_id, db):
    deck = Deck.query.get_or_404(deck_id)
    deck.importing = True
    deck.progress = 0
    db.session.commit()
    import_thread = Thread(target=do_import, args=(deck_id, db))
    import_thread.start()

def do_import(deck_id, db):
    # Implement actual import logic
    pass

def import_progress_logic(deck_id, db):
    deck = Deck.query.get_or_404(deck_id)
    return deck.importing, deck.progress

def all_tags_logic(db):
    all_tags_set = set()
    cards = Card.query.with_entities(Card.tags).all()
    for card in cards:
        if card.tags:
            all_tags_set.update(card.tags.split(','))
    return all_tags_set

def decks_logic(db):
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