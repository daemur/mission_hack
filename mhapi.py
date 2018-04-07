from flask import Flask, request, jsonify
from flask_restful import Resource, Api

from db import recipes

app = Flask(__name__)
api = Api(app)


class Recipes(Resource):
    
    def post(self, recipeName):
        try:
            self.recipe = recipes[recipeName]
        except:
            raise 'Recipe Not Found.'
            
        return jsonify(self.recipe['requirements'])

class Inventory(Resource):
    
    def get(self):
        return None
        
api.add_resource(Recipes, '/recipes/<recipeName>')
api.add_resource(Inventory, '/inventory')
        
if __name__ == '__main__':
     app.run(port=2600)