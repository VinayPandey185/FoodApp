from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps
import json

app = Flask(__name__)
app.secret_key = "foodapp"

# client = MongoClient('localhost', 27017)
# connection = MongoClient("mongodb://localhost:27017/")

client = MongoClient("mongodb+srv://VinayPandey:Vinay185@clusterlzsy5cjj4hru2cyu.cmtwmfg.mongodb.net/?retryWrites=true&w=majority")
print('Ready to Use...')

db = client.FoodMenu
products = db.Products
global_products = products.find()
global_menu = db.Products.distinct("category")
users = db.UserAccount
cartItems = db.Cart
orderPayments = db.OrderAndPayment

foodProducts = ""
foodMenu = ""
global_user = ""
global_user_info = ""
global_message = "Glad you are hear!"


@app.route('/', defaults={'param': "All"})
@app.route('/<param>', methods=['GET', 'POST'])
def home(param):
    if "username" in session:
        _username = session["username"]
        found_user = users.find_one({'userid': _username})
        if found_user:
            find_username = found_user["name"]
            username = find_username
        else:
            username = "Account"

    if param == 'All':
        _products = products.find()

    else:
        _products = products.find({'category': param})

    if "username" in session:
        message = "Glad you are here " + username
        if _username == "admin":
            return render_template('index.html', foodProducts=_products, foodMenu=global_menu,
                                   username=username, orders="Orders",
                                   logout="Sign-out", cart="Cart", insertItem="Manage Products")
        else:
            return render_template('index.html', foodProducts=_products, foodMenu=global_menu,
                                   username=username, orders="Orders",
                                   logout="Sign-out", cart="Cart")

    else:
        return redirect(url_for("signin"))


@app.route('/account_details', methods=['GET', 'POST'])
def account_details():
    if "username" in session:
        username = session["username"]
        user_info = users.find_one({"userid": username})
        if user_info:
            global_user_info = user_info
            return render_template('account.html', user_info=user_info)


@app.route('/account_update', methods=['GET', 'POST'])
def account_update():
    if request.method == 'POST':
        username = request.form.get("username")
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        city = request.form.get("city")
        pin = request.form.get("pin")
        mobile = request.form.get("mobile")

        username = session["username"]

        user_update = users.update_one(
            {"userid": username},
            {"$set":
                 {"password": password,
                  "name": fullname,
                  "email": email,
                  "city": city,
                  "pin": pin,
                  "mobile": mobile}
             })
        user_info = users.find_one({"userid": username})
        if user_update:
            message = "User Details Updated !"
            return render_template('account.html', message=message, className="message", user_info=user_info)
            # return redirect(url_for('account_details'))
        else:
            message = "Something went wrong !"
            return render_template('account.html', message=message, className="error", user_info=global_user_info)
            # return redirect(url_for('account_details'))


@app.route('/account_delete', methods=['GET', 'POST'])
def account_delete():
    message = "Do you really want to delete your account? <a href='/final_delete' class='error'>Yes, Delete</a>"
    username = session["username"]
    user_info = users.find_one({"userid": username})
    return render_template('account.html', message=message, className="error", user_info=user_info)


@app.route('/final_delete', methods=['GET', 'POST'])
def final_delete():
    username = session["username"]
    users.delete_one({"userid": username})
    print("Account Deleted. " + username)
    return redirect(url_for("sign-out"))


# Login with session

@app.route('/logged_in')
def logged_in():
    if "username" in session:
        username = session["username"]
        return redirect(url_for("home"))
    else:
        return redirect(url_for("signin"))


@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if "username" in session:
        return redirect(url_for("logged_in"))

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user_found = users.find_one({'userid': username})
        if user_found:
            found_user = user_found["userid"]
            match_password = user_found['password']

            if password == match_password:
                session["username"] = found_user
                return redirect(url_for('logged_in'))
            else:
                if "username" in session:
                    return redirect(url_for('logged_in'))
                message = 'Wrong Password !'
                return render_template('login.html', message=message, className="error")

        else:
            message = 'User not found !'
            return render_template('login.html', message=message, className="error")

    message = ""
    return render_template('login.html', message=message, className="message")


@app.route("/signout", methods=['GET', 'POST'])
def signout():
    global global_message
    if "username" in session:
        session.pop("username", None)
        global_message = "Signed out successfully."
        # return redirect(url_for("logged_in"))
        return render_template('login.html', message=global_message, className="message")
    else:
        return redirect(url_for("signin"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    message = "from Signup"
    if request.method == 'POST':
        username = request.form.get("username")
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        city = request.form.get("city")
        pin = request.form.get("pin")
        mobile = request.form.get("mobile")

        is_user_in_db = users.find_one({'userid': username})
        is_email_in_db = users.find_one({'email': email})
        if is_user_in_db:
            found_userid = is_user_in_db["userid"]
            message = "You are already registered with : " + str(found_userid)
            if is_email_in_db:
                found_email = is_email_in_db["email"]
                message = str(message) + " (" + str(found_email) + ")"
                return render_template('login.html', message=message, className="error")

        else:
            if username != "" and password != "":
                dict = {
                    "userid": username,
                    "password": password,
                    "name": fullname,
                    "email": email,
                    "city": city,
                    "pin": pin,
                    "mobile": mobile
                }
                db_insert = users.insert_one(dict)
                message = "Your account is created with user id: " + str(username)
                return render_template('login.html', message=message, className="message")
            else:
                message = "Please enter username and password."
                return render_template('login.html', message=message, className="error")
    return render_template('signup.html')


@app.route("/add_to_cart", methods=['GET', 'POST'])
def add_to_cart():
    if "username" in session:
        username = session["username"]
        if request.method == 'POST':
            item_id = int(float(request.form.get("id")))
            item = products.find_one({'id': item_id})
            if item:
                check_cart = cartItems.find_one({'itemid': item_id, 'userid': username})
                if check_cart:
                    # update cart
                    curQty = check_cart['qty']
                    unitPrice = check_cart["unitprice"]
                    totalPrice = str(int(unitPrice) * int((curQty + 1)))
                    message = "Product in cart already"
                    item_update = cartItems.update_one(
                        {"itemid": item_id, 'userid': username},
                        {"$set": {"qty": curQty + 1, "totalprice": totalPrice}})
                    if item_update:
                        return redirect(url_for('logged_in'))
                else:
                    # insert in cart
                    itemDict = {
                        "itemid": item['id'],
                        "userid": session["username"],
                        "itemname": item['name'],
                        "qty": 1,
                        "unitprice": item['price'],
                        "totalprice": item['price'],
                        "image": item['image'],
                    }
                    db_item_insert = cartItems.insert_one(itemDict)
                    if db_item_insert:
                        return redirect(url_for('logged_in'))
                    else:
                        return redirect(url_for('logged_in'))

        all_cart_items = cartItems.find({'userid': username})
        # Calculate final price for all items in cart
        finalcost = 0
        if all_cart_items:
            for item in all_cart_items:
                finalcost = int(finalcost) + int(item['totalprice'])
            _finalcost = "Final Cost: " + str(int(finalcost)) + " ₹"
            all_cart_items_again = cartItems.find({'userid': username})
            if finalcost > 0:
                return render_template('cart.html', className="message", items=all_cart_items_again,
                                       finalcost=_finalcost, intfinalcost=finalcost)
            else:
                return render_template('cart.html', className="message", items=all_cart_items_again)
    else:
        return redirect(url_for('logged_in'))


@app.route("/clear_cart", methods=['GET', 'POST'])
def clear_cart():
    if "username" in session:
        username = session["username"]
        cartItems.delete_many({"userid": username})
        message = 'All items cleared from Cart!'
        totalcost = ""
        return render_template('cart.html', message=message, className="message", totalcost=totalcost)
    else:
        return redirect(url_for('logged_in'))


# checkout
@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    if "username" in session:
        username = session["username"]
        finalcost = request.form.get("finalcost")
        order_item = request.form.get("order_item")
        message = 'Proceed to pay: ' + str(finalcost) + " ₹"
        user_details = users.find_one({'userid': username})
        return render_template('checkout.html', message=message, className="message", userdetails=user_details,
                               finalcost=finalcost, order_item=order_item)
    else:
        return redirect(url_for('logged_in'))


# Buy Now
@app.route("/buynow", methods=['GET', 'POST'])
def buynow():
    if "username" in session:
        username = session["username"]
        id = request.form.get("id")
        itemid = int(float(id))
        order_item = products.find_one({'id': itemid})
        itemname = order_item["name"]
        finalcost = request.form.get("finalcost")
        # order_item = request.form.get("order_item")
        # insert in cart
        itemDict = {
            "itemid": itemid,
            "userid": session["username"],
            "itemname": itemname,
            "qty": 1,
            "unitprice": finalcost,
            "totalprice": finalcost,
            "image": order_item["image"],
        }
        db_item_insert = cartItems.insert_one(itemDict)
        message = 'Proceed to pay: ' + str(finalcost) + " ₹ for " + itemname
        user_details = users.find_one({'userid': username})
        return render_template('checkout.html', message=message, className="message", userdetails=user_details,
                               finalcost=finalcost, order_item=order_item)
    else:
        return redirect(url_for('logged_in'))


# payment
@app.route("/payment", methods=['GET', 'POST'])
def payment():
    global global_message
    if "username" in session:
        username = session["username"]
        recipient_name = request.form.get("recipient_name")
        shipping_address = request.form.get("shipping_address")
        mobile = request.form.get("mobile")

        paid_amount = request.form.get("finalcost")
        card_number = request.form.get("card_number")
        expiry = request.form.get("expiry")
        cvv = request.form.get("cvv")
        name_on_card = request.form.get("name_on_card")

        order_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        order_id = datetime.now().strftime("%d%m%Y%H%M%S")

        card_details = card_number + "_" + expiry + "_" + cvv + "_" + name_on_card
        # order_item = request.form.get("order_item")

        order_item = cartItems.find({'userid': username})
        list_cur = list(order_item)
        # Converting to the JSON
        order_item_json = dumps(list_cur)

        paymentDict = {
            "userid": username,
            "orderid": order_id,
            "order-data": order_date,
            "ordered_items": order_item_json,
            "paid_amount": paid_amount,
            "card_details": card_details,
            "shipping_address": shipping_address,
            "recipient_name": recipient_name,
            "mobile": mobile
        }
        db_item_insert = orderPayments.insert_one(paymentDict)
        if db_item_insert:
            message = 'Congratulations !! Payment done. Order id: ' + order_id
            global_message = message
            clear_cart()
            # return render_template('order_confirmation.html', message=message, className="message", go_back_link="", go_back_text="Go to Home")
            return redirect(url_for('order_confirmation'))
        else:
            message = 'Payment failed !! Please try again. '

            global_message = message
            # return render_template('order_confirmation.html', message=message, className="message", go_back_link="", go_back_text="Go to Home")
            return redirect(url_for('order_confirmation'))
    else:
        return redirect(url_for('logged_in'))


@app.route("/order_confirmation", methods=['GET', 'POST'])
def order_confirmation():
    if "username" in session:
        global global_message
        return render_template('order_confirmation.html', message=global_message, className="message", go_back_link="",
                               go_back_text="Go to Home")
    else:
        return redirect(url_for("signin"))


@app.route("/my_order", methods=['GET', 'POST'])
def my_order():
    global global_message
    if "username" in session:
        username = session["username"]
        global_message = "You have ordered following items till today"
        order_details = orderPayments.find({'userid': username})
        # list_cur = list(order_details)
        # # Converting to the JSON
        # order_details_json = dumps(list_cur)
        return render_template('my_orders.html', message=global_message, className="message",
                               orderdetails=order_details)
    else:
        return redirect(url_for("signin"))


@app.route("/order_details/<order_id>", methods=['GET', 'POST'])
def order_details(order_id):
    global global_message
    if request.method == 'POST':
        if "username" in session:
            username = session["username"]
            global_message = "Find order details for: "
            # order_id = request.form.get("order_id")
            order_details = orderPayments.find_one({'orderid': order_id})


            order_items = order_details["ordered_items"]
            order_items_json = json.loads(order_items)

            return render_template('order_details.html', message=global_message, className="message",
                                   orderdetails=order_items_json, orderid=order_id)
        else:
            return redirect(url_for("signin"))

    order_details = ""
    return render_template('order_details.html', message=global_message, className="message",
                           orderdetails=order_details)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if "username" in session:
        username = session["username"]
        if username == "admin":

            if request.method == 'POST':
                id = request.form.get('id')
                name = request.form.get('name')
                category = request.form.get('category')
                price = request.form.get('price')
                description = request.form.get('description')
                ratings = request.form.get('ratings')
                image = request.form.get('image')

                check_id_in_ProductTable = products.find_one({'id': id})
                if check_id_in_ProductTable:
                   message = "Id exists, please use unique Id."
                   return render_template('admin.html', insert_message=message, className="error")
                else:
                    insertdict = {
                        "id": int(id),
                        "name": name,
                        "category": category,
                        "price": price,
                        "description": description,
                        "ratings": ratings,
                        "image": "images/" + image
                    }
                    db_insert = products.insert_one(insertdict)
                    message = "Successfully Inserted"
                    return render_template('admin.html', insert_message=message, className="message")
            else:
                message = "Insert Product"
                d_message = "Delete Product"
                return render_template('admin.html', insert_message=message, delete_message=d_message)
    return redirect(url_for("logged_in"))


@app.route("/delete_item", methods=['GET', 'POST'])
def delete_item():
    if "username" in session:
        username = session["username"]
        if username == 'admin':
            if request.method == 'POST':
                itemid = request.form.get('id')
                is_deleted = products.delete_one({'id': int(itemid)})
                if is_deleted:
                    message = 'Item deleted'
                    return render_template('admin.html', delete_message=message, className="message")
                else:
                    message = "Item does not exist!"
                    return render_template('admin.html', delete_message=message, className="error")
            else:
                return render_template('admin.html')

        else:
            return redirect(url_for('logged_in'))
    else:
        return redirect(url_for('logged_in'))


if __name__ == "__main__":
    # app.run('localhost', debug=True)
    app.run(debug=False)