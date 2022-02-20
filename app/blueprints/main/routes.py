from .import bp as main
from app import db
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Item, Category, Cart

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html.j2')

@main.route('/listings/<int:id>', methods=['GET','POST'])
def listings(id):
    categories = Category.query.all()
    if id > 0:
        items = Item.query.filter_by(category_id = id).order_by("id")
    else:    
        items = Item.query.order_by("id")
    return render_template('listings.html.j2', categories=categories, items=items)

@main.route('/item/<int:id>', methods=['GET'])
def item(id):
    if current_user:
        item = Item.query.get(id)
        return render_template('item.html.j2', item=item)
    else:
        return redirect(url_for('main.listings'))

@main.route('/additem/<int:id>', methods=['GET','POST'])
@login_required
def additem(id):

    item = Item.query.get(id)
    
    cartitem = Cart.query.get((current_user.id, id))

    if cartitem:
        cartitem.quantity += 1
        cartitem.save()
    else:
        current_user.items.append(item)
        current_user.save()

    flash(f'{item.name} Bridge has been added to your cart.')    

    return render_template('item.html.j2', item=item)

@main.route('/deleteitem/<int:id>', methods=['GET'])
@login_required
def deleteitem(id):
    
    cart_item =  Cart.query.get((current_user.id,id))
    cart_item.delete()
    flash(f'{Item.query.get(id).name.title()} was deleted.')

    return redirect(url_for('main.cart'))

@main.route('/deleteallitem', methods=['GET'])
@login_required
def deleteallitem():
    
    cart_items =  Cart.query.filter_by(user_id=current_user.id)
    if cart_items.count() > 0:
        for cart_item in cart_items:
            cart_item.delete()
        flash('Thanks for your puchase!')
    else:
        flash('Put something in your cart before trying to check out!')

    return redirect(url_for('main.cart'))

@main.route('/cart', methods=['GET'])
@login_required
def cart():

    total=0
    items = db.session.query(Item.id,Item.name,Item.price,Item.desc,Item.img,Cart.quantity).join(Cart).filter_by(user_id=current_user.id).all()
    for item in items:
        total += item.price * item.quantity

    return render_template('cart.html.j2', items=items, total=total)

