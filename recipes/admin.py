from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import HomePage, Recipe, Ingredient

# Unregister the authentication and authorization models
admin.site.unregister(User)
admin.site.unregister(Group)

# Customize admin site headers for a friendlier look
admin.site.site_header = "Westbrook Recipes Admin"
admin.site.site_title = "Westbrook Recipes"
admin.site.index_title = "Welcome to Westbrook Recipes"


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'background_image')
    # You can also add fields in the admin form if needed:
    # fields = ('title', 'background_image')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'meal_type', 'display_favorites')
    list_filter = ('meal_type',)
    filter_horizontal = ('ingredients', 'favorites',)

    def display_favorites(self, obj):
        return ", ".join([user.username for user in obj.favorites.all()])

    display_favorites.short_description = 'Favorites'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
