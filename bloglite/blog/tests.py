from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post, SubPost

User = get_user_model()

class PostAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='testpass')

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_create_post_with_subposts(self):
        url = reverse('post-list')
        data = {
            'title': 'Main Post',
            'body': 'Main body',
            'subposts': [
                {'title': 'Sub 1', 'body': 'Body 1'},
                {'title': 'Sub 2', 'body': 'Body 2'},
            ]
        }

        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(SubPost.objects.count(), 2)

    def test_get_posts(self):
        post = Post.objects.create(title='Hello', body='World', author=self.user)
        SubPost.objects.create(post=post, title='Sub', body='Body')
        url = reverse('post-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['subposts']), 1)

    def test_like_post(self):
        post = Post.objects.create(title='Like this', body='...', author=self.user)
        url = reverse('post-like', kwargs={'pk': post.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['liked'], True)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['liked'], False)

    def test_view_post(self):
        post = Post.objects.create(title='Views', body='...', author=self.user)
        url = reverse('post-view', kwargs={'pk': post.pk})

        self.assertEqual(post.views, 0)

        self.client.get(url)
        post.refresh_from_db()
        self.assertEqual(post.views, 1)

    def test_unauthenticated_create(self):
        self.client.credentials()  
        url = reverse('post-list')
        data = {
            'title': 'No auth',
            'body': 'Should fail',
            'subposts': []
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401) 

