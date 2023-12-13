from django.shortcuts import render , redirect

from shop.form import CustomUserForm
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
import json
from django.http import JsonResponse
from shop.models import Cart
import random




# Create your views here.

def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,'index.html',{"products":products})

def favviewpage(request):
   if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,'fav.html',{"fav":fav})
   else:
    return redirect("/")
   
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")
 


def cart_page(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,'cart.html',{"cart":cart})
  else:
    return redirect("/")

def remove_cart(request,cid):
   cartitem=Cart.objects.get(id=cid)
   cartitem.delete()
   return redirect("/cart")

def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)


def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
     if request.user.is_authenticated:
        data=json.load(request)
        product_qty=(data['product_qty'])
        product_id=(data['pid'])
        #print(request.user.id)
        product_status=Product.objects.get(id=product_id)
        if product_status:
           if Cart.objects.filter(user=request.user.id,product_id=product_id):
              return JsonResponse({'status':'Product Already in cart'},status=200)
           else:
              if product_status.quantity>=product_qty:
                 Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                 return JsonResponse({'status':'Product Add to Cart '},status=200)
              else:
                 return JsonResponse({'status':'Product stock is not available '},status=200)
                 

        return JsonResponse({'status':'Product Add to Cart Success'},status=200)
     else:
        return JsonResponse({'status':'Login to Add Cart'},status=200)
   else:
      return JsonResponse({'status:Invalid Access'},status=200)
    

       

def logout_page(request):
   if request.user.is_authenticated:
      logout(request)
      messages.success(request,"Logged Out Successfully")
   return redirect("/")


def login_page(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
      name=request.POST.get('username')
      pwd=request.POST.get('password')
      user=authenticate(request,username=name,password=pwd)
      if user is not None:
        login(request,user)
        messages.success(request,"Logged in Successfully")
        return redirect("/")
      else:
        messages.error(request,"Invalid User Name or Password")
        return redirect("/login")
    return render(request,"login.html")



def register(request):
    form=CustomUserForm()
    if request.method=='POST':
       form=CustomUserForm(request.POST)
       if form.is_valid():
          form.save()
          messages.success(request,"Registeration Success You Can Login Now...")
          return redirect('/login')
    return render(request,'register.html',{'form':form})

def collections(request):
    category=Category.objects.filter(status=0)
    return render(request,'collections.html',{"category":category})

def collectionsview(request,name):
  if(Category.objects.filter(name=name,status=0)):
     products=Product.objects.filter(category__name=name)
     return render(request,'indes.html',{"products":products,"category_name":name})
  else:
      messages.warning(request,"No Such Catagory Found")
      return redirect('collections')
  
def product_details(request,cname,pname):
   if(Category.objects.filter(name=cname,status=0)):
      if(Product.objects.filter(name=pname,status=0)):
         products=Product.objects.filter(name=pname,status=0).first()
         return render(request,'product_details.html',{"products":products})
      else:
       messages.error(request,"No such category found")
       return redirect('collections')
   else:
     messages.error(request,"No such categort found")
     return redirect('collections')
   


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})



def checkout_page(request):
    rawcart = Cart.objects.filter(user=request.user)

    # Remove items from the cart if the quantity exceeds the available quantity
    for item in rawcart:
        if item.product_qty > item.product.quantity:
            Cart.objects.delete(id=item.id)

    # Retrieve the updated cart items
    Cartitems = Cart.objects.filter(user=request.user)

    # Calculate total price
    total_price = 0
    for item in Cartitems:
        total_price += item.product.selling_price * item.product_qty

    # Create the context dictionary outside of the loop
    context = {'cartitems': Cartitems, 'total_price': total_price}

    return render(request, "checkout.html", context)


def placeorder(request):
   if request.method=='POST':
          neworder=Order()
          neworder.user=request.user
          neworder.fname=request.POST.get('fname')
          neworder.lname=request.POST.get('lname')
          neworder.email=request.POST.get('email')
          neworder.phone=request.POST.get('phone')
          neworder.address=request.POST.get('address')
          neworder.city=request.POST.get('city')
          neworder.state=request.POST.get('state')
          neworder.country=request.POST.get('country')
          neworder.pincode=request.POST.get('pincode')

          neworder.payment_mode=request.POST.get('payment_mode')
          neworder.payment_id=request.POST.get('payment_id')

          cart=Cart.objects.filter(user=request.user)
          cart_total_price=0
          for item in cart:
             cart_total_price= cart_total_price + item.product.selling_price * item.product_qty

          neworder.total_price = cart_total_price
          trackno='customer'+str(random.randint(1111111,9999999))
          while Order.objects.filter(tracking_no=trackno) is None:
              trackno='customer'+str(random.randint(1111111,9999999))

          neworder.tracking_no=trackno 
          neworder.save()


          neworderitems=Cart.objects.filter(user=request.user)
          for item in neworderitems:
             OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
             )
                
               
               

             orderproduct=Product.objects.filter(id=item.product_id).first()
             orderproduct.quantity=orderproduct.quantity-item.product_qty
             orderproduct.save()


          Cart.objects.filter(user=request.user).delete()

          messages.success(request, "your order has been placed successfully")

          payMode=request.POST.get('payment_mode')
          if(payMode == "Paid by Razorpay"):
             return JsonResponse({'status':"your order has been placed successfully"})
          
 
   return redirect('/')



def myorders(request):
   orders=Order.objects.filter(user=request.user)
   context={'orders':orders}
   return render(request,'orders.html',context)


def orderview(request,t_no):
   order=Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
   orderitems=OrderItem.objects.filter(order=order)
   context={'order':order,'orderitems':orderitems}
   return render(request,'view.html',context)

def razorpaycheck(request):
   cart=Cart.objects.filter(user=request.user)
   total_price=0
   for item in cart:
       total_price= total_price + item.product.selling_price * item.product_qty

   return JsonResponse({
      'total_price':total_price
   })


def orders(request):
   return HttpResponse("Thank you...")