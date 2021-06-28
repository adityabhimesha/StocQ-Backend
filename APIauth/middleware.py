class AuthenticateToken:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if(request.path != "api/login/"):
            token = request.COOKIES.get('auth')
            if not token:
                raise AuthenticationFailed('User Not Authenticated!')

            try:
                payload = jwt.decode(token, environ['SECRET'], algorithm=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('User Not Authenticated!!!')

            user_id = payload['id']
            user = User.objects.filter(pk=user_id).first()
            if user is None:
                raise AuthenticationFailed('User Does Not Exist!') 

                
        response = self.get_response(request)
        return response