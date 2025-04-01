from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HomePage, Recipe
from .forms import RecipeForm, IngredientForm
import os
import tempfile
from django.views.decorators.csrf import csrf_exempt

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
    home_page = HomePage.objects.first()  # To maintain the background image
    context = {
        'home_page': home_page,
        'recipes': recipes,
        'meal_filter': "",
        'query': "",
    }
    return render(request, 'recipes/index.html', context)

def custom_404(request, exception):
    return render(request, 'recipes/404.html', status=404)

def test_404(request):
    return render(request, 'recipes/404.html', status=404)

def splash(request):
    # If already configured, send to the main page.
    if os.path.exists("/home/pi/configured.flag"):
        return redirect("index")
    return render(request, "recipes/splash.html")

@csrf_exempt  # For simplicity—ensure proper CSRF handling in production.
def wifi_setup(request):
    if request.method == "POST":
        wifi_type = request.POST.get("wifi_type", "personal")
        ssid = request.POST.get("ssid")
        config_text = ""
        if wifi_type == "personal":
            password = request.POST.get("password")
            config_text = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""
        else:
            # Enterprise configuration
            eap_method = request.POST.get("eap_method", "PEAP")
            identity = request.POST.get("identity", "")
            password = request.POST.get("password")
            config_text = f"""
network={{
    ssid="{ssid}"
    key_mgmt=WPA-EAP
    eap="{eap_method}"
    identity="{identity}"
    password="{password}"
"""
            # If a CA certificate is provided, save it and add to the config.
            ca_cert = request.FILES.get("ca_cert")
            if ca_cert:
                cert_dir = "/etc/wpa_supplicant/certs"
                if not os.path.exists(cert_dir):
                    os.makedirs(cert_dir)
                cert_path = os.path.join(cert_dir, ca_cert.name)
                with open(cert_path, "wb") as f:
                    for chunk in ca_cert.chunks():
                        f.write(chunk)
                config_text += f'    ca_cert="{cert_path}"\n'
            config_text += "}\n"

        try:
            # Write the config text to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp:
                temp.write(config_text)
                temp_filename = temp.name

            # Call the helper script via sudo.
            # Ensure that /usr/local/bin/update_wifi.sh exists and is configured in sudoers for the user 'tyler'
            command = f'sudo /usr/local/bin/update_wifi.sh {temp_filename}'
            os.system(command)

            # Clean up the temporary file
            os.remove(temp_filename)

            # Mark the device as configured.
            with open("/home/tyler/configured.flag", "w") as flag_file:
                flag_file.write("configured")
            return redirect("configured")
        except Exception as e:
            return render(request, "recipes/wifi_setup.html", {"error": str(e)})
    return render(request, "recipes/wifi_setup.html")

def configured(request):
    return render(request, "recipes/configured.html")
