import model

"""Sign-up"""


def create_user(username, password, first_name, last_name):
    """Get form data and add new user to users table"""

    if not password:
        return "Cannot leave password empty"
    if not first_name:
        return "Cannot have first name empty"

    # Check if user exists
    user = model.User.query.filter_by(email=username).first()

    # If user doesn't exist, create user
    if user == None:
        user = model.User(email=username,
                          password=password, first_name=first_name, last_name=last_name)
        model.session.add(user)
        model.session.commit()

        return "Success"

    return "Username already exits"

"""Login"""


def login(username, password):
    """Check if user exists; if exists, authenticate pw and return success msg"""

    user = model.User.query.filter_by(email=username).first()

    if user:
        if user.password == password:
            return user

    return undefined
