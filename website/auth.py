from flask import Blueprint, render_template, request

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html", boolean=False)

@auth.route('/logout')
def logout():
    return "<h1>Logout</h1>"

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        if len(email) < 4:
            pass
        elif len(firstName) < 2:
            pass
        elif password1 != password2:
            #return render_template("signup.html", boolean=True)
            pass
        elif len(password1) < 7:
            pass
        else:
            # Add user to database
            pass

        return render_template("login.html", boolean=False)
    return render_template("signup.html")
