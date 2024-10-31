from django.shortcuts import render,redirect
from shop.models import Category,Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
# Create your views here.
def allcategories(request):
    c=Category.objects.all()
    context={'cat':c}
    return render(request,'category.html',context)

def allproducts(request,p):    # There p receives the category object using id
    c=Category.objects.get(id=p)   # Reads get a particular category
    p=Product.objects.filter(category=c)  # Reads all product under a particular category object
    context={'cat':c,'product':p}

    return render(request,"product.html",context)

def alldetails(request,q):
    p=Product.objects.get(id=q)
    context={'product':p}
    return render(request,"detail.html",context)

def register(request):
    if(request.method=='POST'):
        u=request.POST['u']
        p=request.POST['p']
        cp=request.POST['cp']
        f=request.POST['f']
        l=request.POST['l']
        e=request.POST['e']
        if(p==cp):
           u=User.objects.create_user(username=u,password=p,first_name=f,last_name=l,email=e)
           u.save()
        return redirect('shop:categories')

    return render(request,'register.html')

def user_login(request):
    if (request.method == "POST"):
        u=request.POST['u']
        p=request.POST['p']
        user=authenticate(username=u,password=p)
        if user:
            login(request,user)
            return redirect('shop:categories')
        else:
            messages.error(request,"invalid credentials")
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('shop:login')

def add_category(request):
    if(request.method=="POST"):
        n=request.POST.get('n')
        d=request.POST.get('d')
        i=request.FILES.get('i')
        c=Category.objects.create(name=n,desc=d,image=i)
        c.save()
        return redirect('shop:categories')


    return render(request,'addcategory.html')


def add_product(request):
    if (request.method=="POST"):
        n=request.POST.get('n')
        i=request.FILES.get('i')
        d=request.POST.get('d')
        p=request.POST.get('p')
        s=request.POST.get('s')
        ca=request.POST.get('ca')
        cat=Category.objects.get(name=ca)
        p=Product.objects.create(name=n,image=i,desc=d,price=p,stock=s,category=cat)
        p.save()
        return redirect('shop:categories')

    return render(request,'addproduct.html')


def add_stock(request,i):
    product=Product.objects.get(id=i)
    if(request.method=="POST"):
        product.stock=request.POST['s']
        product.save()
        return redirect('shop:categories')

    context={'pro':product}

    return render(request,'addstock.html',context)