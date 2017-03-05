import model

"""Sign-up"""


def create_user(email, password, first_name, last_name):
    """Get form data and add new user to users table"""

    # Check if user exists
    user = model.User.query.filter_by(email=email).first()

    # If user doesn't exist, create user
    if user == None:
        user = model.User(email=email,
                          password=password, first_name=first_name, last_name=last_name)
        model.session.add(user)
        model.session.commit()

        return "Successfully Added!"

    return "Username already exits"
