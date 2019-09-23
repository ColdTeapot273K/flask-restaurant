from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Restaurants pages

@app.route('/')
@app.route('/restaurants/')
def restaurantsAll():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        restaurantToAdd = Restaurant(name=request.form['name'])
        session.add(restaurantToAdd)
        session.commit()
        flash('New restaurant created!')
        return redirect(url_for('restaurantsAll'))
    if request.method == 'GET':
        return render_template('newRestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurantToEdit = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurantToEdit.name = request.form['name']
        session.add(restaurantToEdit)
        session.commit()
        flash('Restaurant edited!')
        return redirect(url_for('restaurantsAll'))
    if request.method == 'GET':
        return render_template('editRestaurant.html', restaurant=restaurantToEdit)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        session.commit()
        flash('Restaurant deleted!')
        return redirect(url_for('restaurantsAll'))
    if request.method == 'GET':
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)


# Menu pages

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New menu item created!')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    if request.method == 'GET':
        return render_template('newMenuItem.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    itemToEdit = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        session.add(itemToEdit)
        session.commit()
        flash('Menu item edited!')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    if request.method == 'GET':
        return render_template('editMenuItem.html', item=itemToEdit)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu item deleted!')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    if request.method == 'GET':
        return render_template('deleteMenuItem.html', item=itemToDelete)


# Enter API:

@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serialize for i in restaurants])


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menu_id).one()
    return jsonify(MenuItems=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
