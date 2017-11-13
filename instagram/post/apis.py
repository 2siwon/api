# PostList를 리턴하는 APIView를 만드세요
# 근데 APIView를 상속받도록
# get요청만 응답
from rest_framework import generics

from post.models import Post
from post.serializers import PostSerializer


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
