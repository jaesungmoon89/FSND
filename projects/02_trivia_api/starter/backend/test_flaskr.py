import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_getCategories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])
        
    def test_getQuestions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['totalQuestions'])
        
    def test_deleteQuestions(self):
        response = self.client().delete('/questions/39')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 39)
        self.assertTrue(data['totalQuestions'])
        
    def test_deleteQuestions_fail(self):
        response = self.client().delete('/questions/test')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Undefined or not found')
        
    def test_addQuestions(self):
        body = {'question': 'Unit Test Question','answer':'Unit Test Answer','category':1,'difficulty':1}
        response = self.client().post('/questions/add', json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['currentCategory'],1)
        
    def test_getQuestionsBySearchTerm(self):
        body = {'searchTerm': 'Unit Test'}
        response = self.client().post('/questions/search', json=body)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
    
    def test_getQuestionsByCategory(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])   
        
    def test_getQuestionsByCategory_fail(self):
        response = self.client().get('/categories/9999/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unable to process')        
        
    def test_startQuiz(self):
        body = {"quiz_category": 2, "previous_questions":[2,4]}
        response = self.client().post('/quizzes')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['previousQuestions'])
        self.assertTrue(data['currentQuestion'])  
     
       
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()