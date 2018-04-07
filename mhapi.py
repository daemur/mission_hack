from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS

from db import recipes
from cv import FeedEater


feed = FeedEater()
app = Flask(__name__)
api = Api(app)
CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True)

recipe = None
completedSteps = set()

class Recipes(Resource):
    
    def get(self):
        
        feed.set_recipe()
        return jsonify(recipes)

class Recipe(Resource):
    
    def get(self, recipeName):
        
        global recipe
        global completedSteps
        
        for k, v in recipes.items():
            if recipeName.lower() in k.lower():      
                recipe = recipes[recipeName]
                recipe['name'] = recipeName
                feed.set_recipe(recipeName)
        
        for requirement in recipe['requirements']:
            requirement['found'] = requirement['item'] in feed.foundRequirements
            
        for step in recipe['steps']:
            step['done'] = step['name'] in completedSteps
            
        return jsonify(recipe)

class Step(Resource):

    def get(self):
        
        global recipe
        global completedSteps
        
        completedSteps.add(recipe['steps'][len(completedSteps)])
        
api.add_resource(Recipes, '/recipes')
api.add_resource(Recipe, '/recipes/<string:recipeName>')
        
if __name__ == '__main__':
    try:
        #feed.start()
        app.run(port=2600)
    except KeyboardInterrupt:
        feed.stop()