from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart,Payment,Order_details,User
from shop.models import Product
from django.contrib.auth import login

import razorpay
@login_required
def addtocart(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)   # checks the product present in the cart table for a particular user
        if(p.stock>0):
            c.quantity+=1                          # if present it will increment the quantity of product
            c.save()
            p.stock-=1
            p.save()
    except:
        if(p.stock>0): # if not present then it will create a new record inside the cart table with quantity=1
           c=Cart.objects.create(product=p,user=u,quantity=1)
           c.save()
           p.stock-=1
           p.save()


    return redirect('cart:cartview')

def cart_view(request):
    u=request.user
    total=0
    c=Cart.objects.filter(user=u)
    for i in c:
        total+=i.quantity*i.product.price
    context={'cart':c,'total':total}

    return render(request,"cart.html",context)

@login_required
def cart_remove(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        if(c.quantity>1):
            c.quantity-=1
            c.save()
            p.stock+=1
            p.save()
        else:
            c.delete()
            p.stock+=1
            p.save()

    except:
        pass

    return redirect('cart:cartview')

@login_required
def cart_delete(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        if(c.quantity>1):
            c.quantity-=1
            c.save()
            p.stock+=Cart.quantity
            p.save()
        else:
            c.delete()
            p.stock+=Cart.quantity
            p.save()

    except:
        pass

    return redirect('cart:cartview')


@login_required

def checkout_form(request):
    if(request.method=="POST"):
        address=request.POST.get('a')
        phone=request.POST.get('p')
        pin=request.POST.get('pi')

        u=request.user

        c=Cart.objects.filter(user=u)

        total=0

        for i in c:
            total+=i.quantity*i.product.price
        total=int(total*100)

        client=razorpay.Client(auth=('rzp_test_nnlp4dQwHnRlZv','LHgyDXPbArGckg9xRIeeEGIF'))    # create a client connection

            # using razorpay id and secret code

        response_payment=client.order.create(dict(amount=total,currency="INR")) #create an order with
        # razorpay using razorpay client
        # print(response_payment)
        order_id=response_payment['id']
        order_status=response_payment['status']
        if(order_status=="created"):
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=address,phone_no=phone,pin=pin,order_id=order_id)
                o.save()
        else:
            pass

        response_payment['name']=u.username
        context={'payment':response_payment}

        return render(request,'payment.html',context)

    return render(request,'order.html')
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def payment_status(request,u):
    user= User.objects.get(username=u)
    if(not request.user.is_authenticated):  #if user is not authenticated
        login(request,user)  #allowing requset user to login


    if(request.method=="POST"):
        response=request.POST
        print(response)
        print(u)

        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id':response['razorpay_payment_id'],
            'razorpay_signature':response['razorpay_signature']
        }
        client=razorpay.Client(auth=('rzp_test_nnlp4dQwHnRlZv', 'LHgyDXPbArGckg9xRIeeEGIF'))  # create a client connection
        print(client)
        try:
            status=client.utility.verify_payment_signature(param_dict)  #to check the authenticity of the razorpay signature
            print(status)
            # To retrieve a particular record in Payment Table whose order id matches the response order id
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id'] # add the payment id after successful payment
            p.paid=True # changes the pais status to True
            p.save()
            user=User.objects.get(username=u)
            print(user.username)
            o=Order_details.objects.filter(user=user,order_id=response['razorpay_order_id']) # retrieve the records in order_details
            #matching the current user and response_id.
            print(o)
            for i in o:
                i.payment_status="paid"
                i.save()

            #After successful payment deletes the items  in cart for a particular user
            c=Cart.objects.filter(user=user)
            c.delete()

        except:
            pass

    return render(request,'payment_status.html',{'status':status})

@login_required
def your_orders(request):
    u=request.user
    o=Order_details.objects.filter(user=u,payment_status="paid")
    context={'orders':o ,'name':u.username}
    return render(request,'yourorders.html',context)

