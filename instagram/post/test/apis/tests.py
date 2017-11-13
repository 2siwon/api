import filecmp
import io
from random import randint
import requests

import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.storage import get_storage_class
from django.core.files.temp import NamedTemporaryFile
from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APILiveServerTestCase

from post.apis import PostList
from post.models import Post

User = get_user_model()


class PostListViewTest(APILiveServerTestCase):
    URL_API_POST_LIST_NAME = 'api-post'
    URL_API_POST_LIST = '/api/post/'
    VIEW_CLASS = PostList

    @staticmethod
    def create_user(username='dummy'):
        return User.objects.create_user(username=username, age=0)

    @staticmethod
    def create_post(author=None):
        return Post.objects.create(author=author, photo=File(io.BytesIO()))

    def test_post_list_url_name_reverse(self):
        url = reverse(self.URL_API_POST_LIST_NAME)
        self.assertEqual(url, self.URL_API_POST_LIST)

    def test_post_list_url_resolve_view_class(self):

        # /api/post/에 매칭되는 ResolverMatch객체를 가져옴
        resolver_match = resolve(self.URL_API_POST_LIST)
        # ResolverMatch의 url_name이 'api-post'(self.URL_API_POST_LIST_NAME)인지 확인
        self.assertEqual(
            resolver_match.url_name,
            self.URL_API_POST_LIST_NAME)
        # ResolverMatch의 func이 PostList(self.VIEW_CLASS)인지 확인
        self.assertEqual(
            resolver_match.func.view_class,
            self.VIEW_CLASS)

    def test_get_post_list(self):
        user = self.create_user()
        # 0이상 20이하의 임의의 숫자 지정
        num = randint(0, 20)
        # num개수만큼 Post생성, author를 지정해줌
        for i in range(num):
            Post.objects.create(
                author=user,
                photo=File(io.BytesIO()),
            )

        url = reverse(self.URL_API_POST_LIST_NAME)
        # post_list에 GET요청
        response = self.client.get(url)
        # status code가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # objects.count결과가 num과 같은지 확인
        self.assertEqual(Post.objects.count(), num)
        # response로 돌아온 JSON리스트의 길이가 num과 같은지 확인
        self.assertEqual(len(response.data), num)

        # response로 돌아온 객체들이 각각 pk, author, photo, created_at
        for i in range(num):
            cur_post_data = response.data[i]
            self.assertIn('pk', cur_post_data)
            self.assertIn('author', cur_post_data)
            self.assertIn('photo', cur_post_data)
            self.assertIn('created_at', cur_post_data)

    def test_get_post_list_exclude_author_is_none(self):
        """
        post.apis.PostListqbdp 대해
        URL reverse, resolve, 사용하고 있는 view함수가 같은지 확인
        :return:
        """
        user = self.create_user()
        num_author_none_posts = randint(0, 10)
        num_posts = randint(11, 20)

        for i in range(num_author_none_posts):
            self.create_post()
        for i in range(num_posts):
            self.create_post(author=user)

        response = self.client.get(self.URL_API_POST_LIST)
        # author가 없는 Post개수는 response에 포함되지 않는지 확인
        self.assertEqual(len(response.data), num_posts)

    def test_create_post(self):
        """
        Post를 생성하고 생성하기 위해 사용한 파일과 생성되어진 파이링 같은지 검사
        :return:
        """
        # 테스트용 유저 생성
        user = self.create_user()
        # 해당 유저를 현재 client에 강제로 인증
        self.client.force_authenticate(user=user)
        # 테스트용 이미지 파일의 경로
        path = os.path.join(settings.STATIC_DIR, 'test', 'dog04.png')

        # path에 해당하는 파일을 post요청에 'photo'키의 값으로 전달
        with open(path, 'rb') as photo:
            response = self.client.post('/api/post/', {
                'photo': photo,
            })

        # response 코드가 201인지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 1개의 포스트가 생성되었는지 확인
        self.assertEqual(Post.objects.count(), 1)

        # 업로드를 시도한 파일 (path경로의 파일)
        # 실제 업로드 된 파일 (새로 생성된 Post의 photo필드에 있는 파일)이
        # 같은 파일인지 확인

        print(response.data['pk'])
        post = Post.objects.get(pk=response.data['pk'])
        print(path)
        print(post.photo.file.name)

        # print('get_storage_class : {}'.format(get_storage_class(import_path=settings.STATICFILES_STORAGE)))
        if get_storage_class(import_path=settings.STATICFILES_STORAGE):
            # 파일시스템에서의 두 파일을 비교할 경우
            self.assertTrue(filecmp.cmp(path, post.photo.file.name))
        else:
            # S3에 올라간 파일을 비교해야하는 경우
            url = post.photo.url
            # requests를 사용해서 S3파일 URL에 GET요청
            response = requests.get(url)
            # NamedTemporaryFile객체를 temp_file이라는 파일변수로 open
            with NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # temp_file에 response의 내용을 기록
                temp_file.write(response.content)
            # 기록한 temp_file과 원본 path를 비교
            self.assertTrue(filecmp.cmp(path, temp_file.name))

