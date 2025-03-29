from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Recipe, Ingredient

class RecipeForm(forms.ModelForm):
    instructions = forms.CharField(widget=CKEditorWidget(config_name='maximal'))
    meal_type = forms.ChoiceField(
        choices=[
            ('breakfast', 'Breakfast'),
            ('lunch', 'Lunch'),
            ('dinner', 'Dinner'),
            ('dessert', 'Dessert'),
        ],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Recipe
        fields = ['title', 'meal_type', 'instructions', 'ingredients']
        widgets = {
            'ingredients': forms.CheckboxSelectMultiple(),
        }

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name']
