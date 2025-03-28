from django.db import models
from ckeditor.fields import RichTextField

class HomePage(models.Model):
    title = models.CharField(max_length=200, default="Westbrook Recipes")
    background_image = models.ImageField(upload_to='homepage/', blank=True, null=True)

    def __str__(self):
        return self.title

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = RichTextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    instructions = RichTextField()
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')

    def __str__(self):
        return self.title
