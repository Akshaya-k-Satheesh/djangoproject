from shop.models import Category

def menu_links(request):
    c=Category.objects.all()
    return {'links':c}    # We can use this data globally across all webpages inside our app

