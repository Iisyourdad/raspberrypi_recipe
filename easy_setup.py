import os
filename = 'number.txt'
if not os.path.exists(filename):
    with open(filename, 'w') as f:
        f.write('1')
with open(filename, 'r') as f:
    content = f.read().strip()
    try:
        number = float(content)
    except ValueError:
        number = None
if number is not None:
    if number == 1:
        os.system('python -m venv myenv')
        if os.system(r'myenv\Scripts\activate') != 0:
            os.system('source myenv/bin/activate')
        os.system("pip install asgiref Django django-ckeditor django-crispy-forms django-js-asset pillow sqlparse tzdata")
        os.system("python manage.py runserver")
    else:
        if os.system(r'myenv\Scripts\activate') != 0:
            os.system('source myenv/bin/activate')
        os.system("python manage.py runserver")
    with open(filename, 'w') as f:
        f.write(str(number + 1))




#os.system("pip install asgiref, Django, django-ckeditor, django-crispy-forms, django-js-asset, pillow, sqlparse, tzdata")
#os.system("python manage.py runserver")

