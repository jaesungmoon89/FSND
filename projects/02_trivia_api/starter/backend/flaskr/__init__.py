import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories')
  def getCategories():
    print('Get Categories')  
    try:
      categories = Category.query.all()
      catagories_dict = {}
    
      for category in categories:
        catagories_dict[category.id] = category.type
    
      if (len(categories) == 0):
          abort(404)
        
      return jsonify({
        'success': True,
        'categories':catagories_dict,
        'total_categories': len(categories)
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def getQuestions():  
    print('Get Questions')  
    questions = Question.query.all()
        
    categories = Category.query.all()
    catagories_dict = {}
    
    for category in categories:
      catagories_dict[category.id] = category.type
    
    if (len(categories) == 0):
        abort(404)
    
    questions = list(map(Question.format, questions))
    '''formatted_questions = createPagination(request, questions)'''
    
    return jsonify({
      'success': True,
      'questions': questions,
      'categories': catagories_dict,
      'totalQuestions': len(questions)
    })

  def createPagination(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE    
    paginated = [item.format() for item in selection]
    
    return paginated[start:end]    
    

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  def deleteQuestions(q_id):   
    print('Delete Questions')  
    question = Question.query.filter(Question.id==q_id).one_or_none()
    if question is None:
        abort(404)  
        
    question.delete()
    selection = Question.query.order_by(Question.id).all()
    current_questions = createPagination(request, selection)

    return jsonify({
      'success': True,
      'deleted': q_id,
      'questions': current_questions,
      'totalQuestions': len(Question.query.all())
    })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/add', methods=['POST'])
  def addQuestions():
    print('Add Questions')  
    try:
     body = request.get_json()
     new_question = body.get('question',None)
     new_answer = body.get('answer',None)
     new_category = str(body.get('category',None))
     new_difficulty = body.get('difficulty',None)
     question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      
     question.insert()
      
     selection = Question.query.order_by(Question.id).all()
     current_questions = createPagination(request, selection)
      
     return jsonify({
       'success': True,
       'created': question.id,
       'questions': current_questions,
       'totalQuestions': len(Question.query.all()),
       'currentCategory': new_category
     })
    except:
      abort(422)
   
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['OPTIONS'])
  def getQuestionsBySearchTerm():   
    print('Get Questions by Search Term')
    body = request.get_json()
    searchTerm = body.get('searchTerm',None)
    
    question = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
    try:
     if question is None:
        abort(404)  
     current_questions = createPagination(request, question)
       
     if (len(current_questions) == 0):
        abort(404)  

     return jsonify({
      'success': True,
      'questions': current_questions,
      'totalQuestions': len(Question.query.all()),
      'currentCategory': ''
     })
    except:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:c_id>/questions', methods=['GET'])
  def getQuestionsByCategory(c_id):   
    print('Get Questions by Category')  
    question = Question.query.filter(Question.category==c_id).all()
    if question is None:
        abort(404)  
    current_questions = createPagination(request, question)
       
    if (len(current_questions) == 0):
        abort(404)  

    return jsonify({
      'success': True,
      'questions': current_questions,
      'totalQuestions': len(current_questions),
      'currentCategory': ''
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def startQuiz():   
    print('start Quiz')  
    body = request.get_json()
    previous_questions = body.get('previous_questions',None)
    quiz_category = body.get('quiz_category',None)
    
    if (quiz_category == 0):
     quiz = Question.query.all()
    else:
     quiz = Question.query.filter_by(category=quiz_category).all()
    
    if quiz is None:
        abort(404)
    selected_questions = []
    
    for question in quiz:
     if (question.id not in previous_questions):
        selected_questions.append(question.format())
    
    if len(selected_questions) > 0:
        next_question = random.choice(selected_questions)
        return jsonify({
          'success': True,
          'previousQuestions': previous_questions,
          'currentQuestion': next_question
          })
    else:
        return jsonify({
          'success': True
        })    

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    