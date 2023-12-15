from models import db, User, Deck, Card, Session, History, Deck_Status, Card_Status
from app import app  # Ensure this imports your Flask app

def dump_model_contents(model):
    for item in model.query.all():
        print(f"{model.__name__} {item.id}:")
        for key, value in item.__dict__.items():
            if not key.startswith('_'):
                print(f"  {key}: {value}")
        print()

def dump_database_contents():
    with app.app_context():
        dump_model_contents(User)
        dump_model_contents(Deck)
        dump_model_contents(Card)
        dump_model_contents(Session)
        dump_model_contents(History)
        dump_model_contents(Deck_Status)
        dump_model_contents(Card_Status)

if __name__ == "__main__":
    dump_database_contents()