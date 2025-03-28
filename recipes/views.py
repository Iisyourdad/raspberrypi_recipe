from django.shortcuts import render, redirect
from django.db.models import Q
from .models import HomePage, Recipe
from .forms import RecipeForm, IngredientForm
from django.contrib import messages

def index(request):
    home_page = HomePage.objects.first()
    recipes = Recipe.objects.all()
    query = request.GET.get('q')
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(instructions__icontains=query) |
            Q(ingredients__name__icontains=query)
        ).distinct()
    context = {
        'home_page': home_page,
        'recipes': recipes,
        'query': query or "",
    }
    return render(request, 'recipes/index.html', context)

# (Other views unchanged)
def add_recipe(request):
    form = RecipeForm()
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Recipe created successfully!")
            return redirect("index")
    context = {'form': form}
    return render(request, "recipes/add_recipe.html", context)

def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = IngredientForm()
    return render(request, 'recipes/add_ingredient.html', {'form': form})
