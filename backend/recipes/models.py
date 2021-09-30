from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class ColorFieldButUnique(ColorField):

    def __init__(self, *args, **kwargs):
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)


class Tag(models.Model):
    title = models.CharField(verbose_name="Название",
                             help_text="Название тега", unique=True,
                             max_length=100)
    color_code = ColorFieldButUnique(default='#FF0000')
    slug = models.SlugField(verbose_name="Слаг", unique=True)

    class Meta:
        ordering = ['id', ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField(verbose_name="Название",
                             help_text="Название ингредиента", max_length=100)
    units = models.CharField(verbose_name="Единицы измерения",
                             help_text="Единицы измерения для ингредиента",
                             max_length=100)

    class Meta:
        ordering = ['title', ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.title} {self.units}'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="recipes", verbose_name="Автор",
                               help_text="Выбор из существующих пользователей")
    title = models.CharField(verbose_name="Название",
                             help_text="Название рецепта", max_length=100)
    image = models.ImageField(upload_to='recipes/images',
                              blank=True, null=True,
                              verbose_name="Картинка к рецепту",
                              help_text="Загрузить выбранную")
    description = models.TextField(verbose_name="Описание",
                                   help_text="Описание рецепта")
    ingredients = models.ManyToManyField("Ingredient",
                                         verbose_name="Ингредиенты",
                                         help_text="Выбор из "
                                                   "существующих ингредиентов",
                                         through="IngredientInRecipe")
    tags = models.ManyToManyField("Tag",
                                  through='ReceiptTag',
                                  verbose_name="Теги",
                                  help_text="Выбор из существующих тегов")
    time = models.PositiveSmallIntegerField(verbose_name="Время приготовления",
                                            validators=[MinValueValidator(1)],
                                            help_text="Время необходимое для "
                                                      "приготовления рецепта")
    pub_date = models.DateTimeField(verbose_name="Дата публикации",
                                    auto_now_add=True,
                                    help_text="Автоматически заполняется "
                                              "сегодняшней датой",
                                    db_index=True)

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.author}: {self.title}'


class IngredientInRecipe(models.Model):
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
