from django.db import models
from django.contrib.auth.models import User

class HomePage(models.Model):
    title = models.CharField(max_length=200, default="Westbrook Recipes")
    background_image = models.ImageField(upload_to="backgrounds/", blank=True, null=True)

    def __str__(self):
        return self.title

class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('dessert', 'Dessert'),
    ]
    title = models.CharField(max_length=200)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES, default='breakfast')
    instructions = models.TextField()
    ingredients = models.ManyToManyField(Ingredient)
    favorites = models.ManyToManyField(User, related_name='favorite_recipes', blank=True)

    def __str__(self):
        return self.title
