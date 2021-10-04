from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='Название тега',
                            max_length=100)
    color = ColorField()
    slug = models.SlugField(verbose_name='Слаг')

    class Meta:
        ordering = ['id', ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название ингредиента',
                            max_length=100)
    measurement_unit = models.CharField(verbose_name='Единицы измерения '
                                                     'для ингредиента',
                                        max_length=100)

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор',
                               help_text='Выбор из существующих пользователей')
    name = models.CharField(verbose_name='Название',
                            help_text='Название рецепта', max_length=100)
    image = models.ImageField(upload_to='recipes/images',
                              verbose_name='Картинка к рецепту',
                              help_text='Загрузить выбранную')
    text = models.TextField(verbose_name='Описание',
                            help_text='Описание рецепта', max_length=10000)
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты',
                                         help_text='Выбор из '
                                                   'существующих ингредиентов',
                                         through='RecipeIngredient')
    tags = models.ManyToManyField(Tag,
                                  through='ReceiptTag',
                                  verbose_name='Теги',
                                  help_text='Выбор из существующих тегов')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Время необходимое для приготовления рецепта'
    )
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True,
                                    help_text='Автоматически заполняется '
                                              'сегодняшней датой',
                                    db_index=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.author}: {self.name}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe'
            )
        ]


class ReceiptTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Теги'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_tagging'
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User, verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} following {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites',
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Избранные'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )]

    def __str__(self):
        return f'{self.user} added {self.recipe}'
