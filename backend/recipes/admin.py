from django.contrib import admin

from .models import Recipe, Ingredient, Tag, ShoppingCart, Favorite


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ('author',
              'name',
              'image',
              'text',
              'cooking_time',
              )
    readonly_fields = (
        'pub_date',
    )
    list_filter = (
        'author',
        'name',
    )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'measurement_unit'
    )
    list_filter = (
        'name',
    )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'color',
        'slug'
    )
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        'added_date'
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        'added_date'
    )
