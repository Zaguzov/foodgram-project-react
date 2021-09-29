from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from users.serializers import UserDetailSerializer
from .fields import Base64ImageField
from .models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    ReceiptTag,
    Follow,
    Favorite,
    ShoppingCart
)

User = get_user_model()


class ShowRecipeAddedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'title',
            'image',
            'time'
        )
        read_only_fields = fields

    def get_image(self, obj):
        request = self.context.get('request')
        photo_url = obj.image.url
        return request.build_absolute_uri(photo_url)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'title',
            'color_code',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'title',
            'units'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    title = serializers.ReadOnlyField(source='ingredient.title')
    unit = serializers.ReadOnlyField(
        source='ingredient.units'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'title',
            'units',
            'amount'
        )

    def get_ingredients(self, obj):
        qs = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(qs, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj,
                                       user=request.user).exists()

    def get_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj,
                                           user=request.user).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount'
        )


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserDetailSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'title',
            'image',
            'description',
            'time'
        )

    def get_ingredients(self, obj):
        record = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(
            record,
            many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(
            recipe=obj,
            user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=user).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=300,
        use_url=True
    )
    author = UserDetailSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'title',
            'image',
            'description',
            'time'
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for item in ingredients:
            if int(item['amount']) < 0:
                raise serializers.ValidationError(
                    {'ingredients': ('Убедитесь, что значение количества '
                                     + 'ингредиента больше 0')})
        return data

    def validate_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Введите целое число больше 0 для времени готовки'
            )
        return data

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients_data:
            ingredient_model = ingredient['id']
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_model,
                recipe=recipe,
                amount=amount
            )
        for tag in tags_data:
            ReceiptTag.objects.create(recipe=recipe, tag=tag)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        ReceiptTag.objects.filter(recipe=instance).delete()
        for tag in tags_data:
            ReceiptTag.objects.create(
                recipe=instance,
                tag=tag
            )
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        for new_ingredient in ingredient_data:
            IngredientInRecipe.objects.create(
                ingredient=new_ingredient['id'],
                recipe=instance,
                amount=new_ingredient['amount']
            )
        instance.title = validated_data.pop('title')
        instance.description = validated_data.pop('description')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.time = validated_data.pop('time')
        instance.save()
        return instance

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = data['recipe'].id

        if (self.context.get('request').method == 'GET'
                and Favorite.objects.filter(
                    user=user,
                    recipe__id=recipe_id).exists()):
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное')

        recipe = get_object_or_404(Recipe, id=recipe_id)

        if (self.context.get('request').method == 'DELETE'
                and not Favorite.objects.filter(
                    user=user,
                    recipe=recipe).exists()):
            raise serializers.ValidationError(
                'Такого рецепта не существует')

        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeAddedSerializer(
            instance.recipe,
            context=context).data


class ShoppingCartSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = data['recipe'].id
        if (self.context.get('request').method == 'GET'
                and ShoppingCart.objects.filter(
                    user=user,
                    recipe__id=recipe_id).exists()):
            raise serializers.ValidationError(
                'Продукты уже в корзине')

        recipe = get_object_or_404(Recipe, id=recipe_id)

        if (self.context.get('request').method == 'DELETE'
                and not ShoppingCart.objects.filter(
                    user=user,
                    recipe=recipe).exists()):
            raise serializers.ValidationError(
                'Такого рецепта нет в списке покупок')
        return data


class ShowFollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count')
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.follower.filter(
            user=obj,
            author=request.user).exists()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:settings.RECIPES_LIMIT]
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeAddedSerializer(
            recipes,
            many=True,
            context=context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = (
            'user',
            'author'
        )

    def validate(self, data):
        user = self.context.get('request').user
        author_id = data['author'].id
        follow_exist = Follow.objects.filter(
            user=user,
            author__id=author_id).exists()

        if self.context.get('request').method == 'GET':
            if user.id == author_id or follow_exist:
                raise serializers.ValidationError(
                    'Подписка существует')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowFollowSerializer(
            instance.author,
            context=context).data