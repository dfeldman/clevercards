import unittest
from app import app, db  # Import your Flask app and db object
from models import User, Deck, Card, init_db # Import necessary models

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a test database
        with app.app_context():
            db.create_all()  # Create tables for testing
            init_db(app)
            self.populate_test_data()  # Populate test data

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def populate_test_data(self):
        # Create and add test data to the database
        user = User(name="testuser")
        deck = Deck(name="Test Deck", user=user)
        card = Card(front="Front", back="Back", deck=deck)
        db.session.add_all([user, deck, card])
        db.session.commit()

    def test_add_deck(self):
        response = self.app.post('/api/add_deck', json={'name': 'New Test Deck'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('deck_id', response.json)

    def test_delete_deck(self):
        response = self.app.delete('/api/delete_deck/1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])

    def test_add_card(self):
        response = self.app.post('/api/add_card/1', json={'front': 'New Front', 'back': 'New Back'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('card_id', response.json)

    def test_edit_card(self):
        response = self.app.put('/api/edit_card/1', json={'front': 'Updated Front', 'back': 'Updated Back'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('card_id', response.json)

    def test_review_session(self):
        # Start a review session
        response = self.app.get('/review/1')
        self.assertEqual(response.status_code, 200)
        # This assumes the presence of HTML content for the review page

    def test_submit_review(self):
        response = self.app.post('/submit_review', data={'card_id': 1, 'status': 'Easy', 'session_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])

    # def test_import_deck(self):
    #     # Assuming an import_deck endpoint that triggers an import process
    #     response = self.app.post('/import_deck/1')
    #     self.assertEqual(response.status_code, 302)  # Redirect to main screen

    # def test_import_progress(self):
    #     response = self.app.get('/import_progress/1')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('importing', response.json)
    #     self.assertIn('progress', response.json)

    def test_all_tags(self):
        response = self.app.get('/tags')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

if __name__ == '__main__':
    unittest.main()
