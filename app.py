from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "taxi-secret-key")  

@app.route("/", methods=["GET"])
def index():
    session.clear()
    return render_template("index.html",
                           state="set_fare")   


@app.route("/set_fare", methods=["POST"])
def set_fare():
    taxi_fare = request.form.get("taxi_fare", "")

    try:
        taxi_fare = float(taxi_fare)
        if taxi_fare <= 0:
            raise ValueError
    except ValueError:
        return render_template("index.html",
                               state="set_fare",
                               error="Enter a valid taxi fare.")

    session["taxi_fare"]         = taxi_fare
    session["total_drivers_money"] = 0.0
    session["total_passengers"]  = 0
    session["counter"]           = 1
    session["log"]               = []

    return render_template("index.html",
                           state="payment",
                           taxi_fare=taxi_fare,
                           counter=1)


@app.route("/calculate", methods=["POST"])
def calculate():
    taxi_fare = session.get("taxi_fare")
    counter   = session.get("counter", 1)
    log       = session.get("log", [])

    amount_paid         = request.form.get("amount_paid", "")
    number_of_passengers = request.form.get("number_of_passengers", "")

    try:
        amount_paid = float(amount_paid)
        if amount_paid < 0:
            raise ValueError
    except ValueError:
        return render_template("index.html",
                               state="payment",
                               taxi_fare=taxi_fare,
                               counter=counter,
                               log=log,
                               total_drivers_money=session.get("total_drivers_money", 0),
                               total_passengers=session.get("total_passengers", 0),
                               error="Enter a valid amount paid.")

    try:
        number_of_passengers = int(number_of_passengers)
        if number_of_passengers < 1:
            raise ValueError
    except ValueError:
        return render_template("index.html",
                               state="payment",
                               taxi_fare=taxi_fare,
                               counter=counter,
                               log=log,
                               total_drivers_money=session.get("total_drivers_money", 0),
                               total_passengers=session.get("total_passengers", 0),
                               error="Enter at least 1 passenger.")

    drivers_money = taxi_fare * number_of_passengers
    change        = amount_paid - drivers_money

    session["total_drivers_money"] = session.get("total_drivers_money", 0) + drivers_money
    session["total_passengers"]    = session.get("total_passengers", 0) + number_of_passengers

    log.append({
        "counter":    counter,
        "pax":        number_of_passengers,
        "paid":       amount_paid,
        "drivers_money": drivers_money,
        "change":     change,
    })
    session["log"]     = log
    session["counter"] = counter + 1
    session.modified = True

    return render_template("index.html",
                           state="prompt",
                           taxi_fare=taxi_fare,
                           counter=counter,
                           log=log,
                           total_drivers_money=session["total_drivers_money"],
                           total_passengers=session["total_passengers"])


@app.route("/add_group", methods=["POST"])
def add_group():
    return render_template("index.html",
                           state="payment",
                           taxi_fare=session.get("taxi_fare"),
                           counter=session.get("counter", 1),
                           log=session.get("log", []),
                           total_drivers_money=session.get("total_drivers_money", 0),
                           total_passengers=session.get("total_passengers", 0))


@app.route("/finish", methods=["POST"])
def finish():
    return render_template("index.html",
                           state="done",
                           taxi_fare=session.get("taxi_fare"),
                           log=session.get("log", []),
                           total_drivers_money=session.get("total_drivers_money", 0),
                           total_passengers=session.get("total_passengers", 0))


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
