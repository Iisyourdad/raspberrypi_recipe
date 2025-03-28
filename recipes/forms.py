from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Recipe, Ingredient



class RecipeForm(forms.ModelForm):
    instructions = forms.CharField(widget=CKEditorWidget(config_name='maximal'))

    class Meta:
        model = Recipe
        fields = ['title', 'instructions', 'ingredients']
        widgets = {
            'ingredients': forms.CheckboxSelectMultiple(),
        }


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name']
