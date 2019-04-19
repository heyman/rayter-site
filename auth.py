from flask_basicauth import BasicAuth

class Auth(BasicAuth):
    def __init__(self, app, users_conf):
        """ Takes a Flask app and a string of users and passwords formatted like this:
            user1:password1,user2:password2,...
            
            Used like this:
            
            auth = Auth(app, "...")

            @app.route("/something")
            @auth.required
            def something():
            """
        super(Auth, self).__init__(app)
        self.users = {}
        for user_conf in users_conf.split(','):
            (user, password) = user_conf.split(':')
            self.users[user] = password

    def check_credentials(self, username, password):
        match = self.users.get(username) == password
        return match is True
