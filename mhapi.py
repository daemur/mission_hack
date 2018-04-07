from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS

from db import recipes

app = Flask(__name__)
api = Api(app)
CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True)

class Recipes(Resource):
    
    def get(self):
        
        return jsonify(recipes)

class Recipe(Resource):
    
    def get(self, recipeName):
        
        self.recipe = recipes[recipeName]
        return jsonify(self.recipe['requirements'])

class Inventory(Resource):
    
    def get(self):
        return None
        
api.add_resource(Recipes, '/recipes/')
api.add_resource(Recipe, '/recipes/<recipeName>')
api.add_resource(Inventory, '/inventory')
        
if __name__ == '__main__':
     app.run(port=2600)