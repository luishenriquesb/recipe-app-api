from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializer


class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializer.TagSerializer

    
class IngredientViewSet(BaseRecipeAttrViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializer.IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class=serializer.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializer.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializer.RecipeImageSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
    
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )