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
    list_display = ('title',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title',)
    filter_horizontal = ('ingredients',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
