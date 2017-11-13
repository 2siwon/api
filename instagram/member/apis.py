from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token


class Login(APIView):
    def post(self, request, *args, **kwargs):
        # 1. username/password를 받음
        # 2. authenticate를 이용해 사용자 인증
        # 3. 인증된 사용자에 해당하는 토큰을 생성
        # 4. 사용자 정보와 token.key값을 Response로 돌려줌
        print(request.data)
        username = request.data['username']
        password = request.data['password']

        user = authenticate(
            username=username,
            password=password,
        )
        # user가 존재할 경우 (authenticate에 성공)
        if user:
            # 'user'키에 다른 dict로 유저에 대한 모든 정보를 보내줌
            token, token_created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'user': {
                    'pk': user.pk,
                    'username': user.username,
                    'img_profile': user.img_profile.url if user.img_profile else '',
                    'age': user.age,
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        # 인증에 실패한 경우
        data = {
            'message': 'Invalid credentials'
        }
        return Response(data, status=status.HTTP_401_UNAUTHORIZED)
