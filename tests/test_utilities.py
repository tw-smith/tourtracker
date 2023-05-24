def login_helper(self, email, password):
    return self.client.post('/auth/login', data={
        'email': email,
        'password': password,
    }, follow_redirects=True)


def logout_helper(self):
    return self.client.get('/auth/logout', follow_redirects=True)
