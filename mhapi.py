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

class Recipes(Resource):
    
    def get(self):
        
        feed.set_recipe()
        return jsonify(recipes)

class Recipe(Resource):
    
    def get(self, recipeName):
        
        global recipe
        
        if recipe == None or recipe['name'] != recipeName:
            for k, v in recipes.items():
                if recipeName.lower() in k.lower():      
                    recipe = recipes[recipeName]
                    recipe['name'] = recipeName
                    feed.reset_found_requirements()
                    feed.set_requirements([x['name'] for x in recipe['requirements'])
        
            recipe['steps'][0]['currentStep'] = True
        
        for requirement in recipe['requirements']:
            requirement['found'] = requirement['item'] in feed.foundRequirements
           
        #test
        recipe['requirements'][1]['found'] = True
            
        return jsonify(recipe)

class Step(Resource):

    def get(self, id):
        
        global recipe

        recipe['steps'][id]['currentStep'] = True
        if recipe['steps'][id - 1]:
            recipe['steps'][id - 1]['currentStep'] = False
            recipe['steps'][id - 1]['completed'] = True
        
        feed.set_requirements([x for x in recipe['steps'][id]['item']])
            
        return jsonify(recipe['steps'][id])
        
api.add_resource(Recipes, '/recipes')
api.add_resource(Recipe, '/recipes/<string:recipeName>')
api.add_resource(Step, '/step/<int:id>')
        
if __name__ == '__main__':
    try:
        #feed.start()
        app.run(port=2600)
    except KeyboardInterrupt:
        feed.stop()