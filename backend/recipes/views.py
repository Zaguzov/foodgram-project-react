from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter, IngredientFilter
from .models import (Tag,
                     Ingredient,
                     Recipe,
                     Favorite,
                     ShoppingCart,
                     IngredientInRecipe,
                     Follow
                     )
from .paginators import CustomPageNumberPaginator
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          ShowRecipeSerializer,
                          CreateRecipeSerializer,
                          FavoriteSerializer,
                          ShoppingCartSerializer,
                          ShowFollowSerializer,
                          FollowSerializer
                          )

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AdminOrAuthorOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPaginator

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        get_object_or_404(
            Favorite,
            user=user,
            recipe__id=recipe_id).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ShoppingCartViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }

        context = {'request': request}
        serializer = ShoppingCartSerializer(
            data=data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        get_object_or_404(
            ShoppingCart,
            user=user,
            recipe__id=recipe_id).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        shopping_cart = request.user.shopping_cart.all()
        buying_list = {}

        for item in shopping_cart:
            ingredients = IngredientInRecipe.objects.filter(
                recipe=item.recipe
            )
            for ingredient in ingredients:
                amount = ingredient.amount
                title = ingredient.ingredient.title
                units = ingredient.ingredient.units

                if title not in buying_list:
                    buying_list[title] = {
                        'units': units,
                        'amount': amount
                    }
                else:
                    buying_list[title]['amount'] = (buying_list[title]['amount']
                                                   + amount)

        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["amount"]} '
                            f'{buying_list[item]["units"]} \n')

        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = ShowFollowSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class FollowViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, author_id):
        user = request.user

        data = {
            'user': user.id,
            'author': author_id
        }
        serializer = FollowSerializer(
            data=data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        obj = get_object_or_404(
            Follow,
            user=user,
            author__id=author_id
        )
        obj.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )