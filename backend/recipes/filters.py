from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


User = get_user_model()


class RecipeFilter(filters.FilterSet):
    """Фильтр для модели Recipe"""
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset

@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
def download_shopping_cart(self, request):
    """
    Генерация списка покупок в текстовом файле.
    """
    ingredients = (
        Recipe.objects
        .filter(shoppingcart__user=request.user)
        .values('ingredients__name', 'ingredients__measurement_unit')
        .annotate(total=Sum('recipeingredient__amount'))
        .order_by('ingredients__name')
    )

    lines = ['Список покупок:\n']
    for item in ingredients:
        name = item['ingredients__name']
        unit = item['ingredients__measurement_unit']
        amount = item['total']
        lines.append(f'- {name} ({unit}) — {amount}')

    content = '\n'.join(lines)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
    return response