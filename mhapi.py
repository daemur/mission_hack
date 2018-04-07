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

class Recipes(Resource):
    
    def get(self):
        
        feed.set_recipe()
        return jsonify(recipes)

class Recipe(Resource):
    
    def get(self, recipeName):
        
        for k, v in recipes.items():
            if recipeName.lower() in k.lower():      
                self.recipe = recipes[recipeName]
                self.recipe['name'] = recipeName
                feed.set_recipe(recipeName)
                
        return jsonify(self.recipe)

class Inventory(Resource):
    
    def get(self):
        return None
        
api.add_resource(Recipes, '/recipes/')
api.add_resource(Recipe, '/recipes/<string:recipeName>')
api.add_resource(Inventory, '/inventory')
        
if __name__ == '__main__':
    try:
        feed.start()
        app.run(port=2600)
    except KeyboardInterrupt:
        feed.stop()