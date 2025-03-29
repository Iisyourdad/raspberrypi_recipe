from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HomePage, Recipe
from .forms import RecipeForm, IngredientForm

def index(request):
    home_page = HomePage.objects.first()
    recipes = Recipe.objects.all()
    query = request.GET.get('q')
    meal_filter = request.GET.get('meal')
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(instructions__icontains=query) |
            Q(ingredients__name__icontains=query)
        ).distinct()
    if meal_filter:
        recipes = recipes.filter(meal_type=meal_filter)
    context = {
        'home_page': home_page,
        'recipes': recipes,
        'query': query or "",
        'meal_filter': meal_filter or "",
    }
    return render(request, 'recipes/index.html', context)

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

@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    if user in recipe.favorites.all():
        recipe.favorites.remove(user)
        messages.success(request, f"Removed '{recipe.title}' from your favorites.")
    else:
        recipe.favorites.add(user)
        messages.success(request, f"Added '{recipe.title}' to your favorites.")
    return redirect('index')

@login_required
def favorites(request):
    user = request.user
    recipes = Recipe.objects.filter(favorites=user)
    home_page = HomePage.objects.first()  # Include the HomePage to maintain the background image
    context = {
        'home_page': home_page,
        'recipes': recipes,
        'meal_filter': "",
        'query': "",
    }
    return render(request, 'recipes/index.html', context)


from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'recipes/404.html', status=404)

def test_404(request):
    return render(request, 'recipes/404.html', status=404)

