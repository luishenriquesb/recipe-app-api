from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializer import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTest(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'teste@teste',
            'passw1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user,name='Vegan')
        Tag.objects.create(user=self.user,name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_tags_limited_to_user(self):
        user1 = get_user_model().objects.create_user(
            'teste1@user.gov.br',
            'testpass'
        )
        Tag.objects.create(user=user1, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Confort food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'], tag.name)