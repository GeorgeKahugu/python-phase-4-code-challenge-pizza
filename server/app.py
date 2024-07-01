from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"

class RestaurantsResource(Resource):
    def get(self):
        try:
            restaurants = Restaurant.query.all()
            return [restaurant.to_dict(include_relationships=False) for restaurant in restaurants], 200
        except Exception as e:
            app.logger.error(f"Error fetching restaurants: {e}")
            return {"error": str(e)}, 500

    def post(self):
        data = request.get_json()
        restaurant = Restaurant(name=data['name'], address=data['address'])
        db.session.add(restaurant)
        db.session.commit()
        return restaurant.to_dict(), 201
class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(), 200

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

class PizzasResource(Resource):
    def get(self):
        try:
            pizzas = Pizza.query.all()
            return [pizza.to_dict() for pizza in pizzas], 200
        except Exception as e:
            app.logger.error(f"Error fetching pizzas: {e}")
            return {"error": str(e)}, 500

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data['price']
            pizza_id = data['pizza_id']
            restaurant_id = data['restaurant_id']

            if not (1 <= price <= 30):
                return {"errors": ["validation errors"]}, 400

            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            return restaurant_pizza.to_dict(), 201
        except KeyError as e:
            return {"errors": f"Missing key: {e.args[0]}"}, 400
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return {"errors": str(e)}, 500

api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')

if __name__ == "main":
    app.run(port=5555, debug=True)