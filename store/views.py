from datetime import datetime

import math

import random
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Cart, Category, CustomUser, Sale, Product, cartItem
from .forms import PurchaseProductForm, UserCreationForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Sum
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    today = datetime.today()
    year = today.year
    month = today.month
    day = today.day
    today = Sale.objects.filter(
        date_created__year = year,date_created__month=month, 
        date_created__day=day
        ).aggregate(Sum('total_price'), Sum('total_profit'), Sum('quantity'))
    context = {'today':today,'user':request.user}
    return render(request, 'home.html', context)

def base(request):
    return render(request, 'main/base.html')

def signup(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully !')
            return redirect("store:signin")
        else:
            messages.error(request, 'Something went wrong. Please fixe the below errors')

    context = {'form':form}
    return render(request, 'signup.html', context)
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            if user.last_login:
                messages.success(request, f"Welcome Back {user.first_name} {user.last_name}")
            else:
                messages.success(request, f"Welcome {user.first_name} {user.last_name}")
            return redirect("home")
        else:
            messages.error(request, 'The username or password is incorrect !')

    context= {}
    return render(request, 'signin.html', context)
@login_required
def sales(request):
    product = Product.objects.select_related('category')
    # setting up paginator
    p = Paginator(product, 5)
    #creating paginator
    page_number = request.GET.get('page')
    #getting the desire page number from the url
    try:
        page_obj = p.get_page(page_number)
        #return the desire page object
    except PageNotAnInteger:
        page_obj = p.page(1)
        #if page number is not an integer then assign the first page 
    except EmptyPage:
        #if the page i empty then return the last page
        page_obj = p.page(p.num_pages)
    context = {'page_obj':page_obj}
    return render(request, 'sales.html',context)

def signout(request):
    logout(request)
    messages.success(request, "You've been successfully logged out.")
    return render(request, 'home.html')

def product(request):
    if request.method == 'POST':
        id = request.POST['getid']
        Product.objects.filter(id=id).delete()
        messages.success(request, "Item Deleted Successfully !")
    product = Product.objects.all().order_by('-id')
    #Paginator start
    p = Paginator(product, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    # paginator end
    context = {'page_obj':page_obj,'flag':'list'}
    return render(request, 'product.html', context)


def purchase(request):
    purchase_form = PurchaseProductForm()
    if request.method == 'POST':
        purchase_form = PurchaseProductForm(request.POST, request.FILES)
        
        if purchase_form.is_valid():
            price = purchase_form.cleaned_data.get('price')
            quantity = purchase_form.cleaned_data.get('quantity')
            total_price = purchase_form.cleaned_data.get('bulk_price')
            rate  = round((total_price / quantity),3)
            profit = round((price - rate),3)
            stock = quantity
            print(f"RATE: {rate} || PROFIT: {profit} || STOCK: {stock}")
            product = purchase_form.save(commit=False)
            product.rate = rate
            product.profit = profit
            product.stock = stock
            product.user = request.user
            product.save()
            messages.success(request, "Product added successfully !")
        else:
            messages.error(request, f"Something went wrong. Please fix the below errors.{purchase_form.errors}")

        
    product = Product.objects.all().order_by('-id')
    #Paginator start
    p = Paginator(product, 5 )
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    #Paginator end
    number = []
    for x in range(1, 100,1):
        number.append(x)
    cat = Category.objects.all()
    context = {
        'category':cat,
        'page_obj':page_obj,
        'num':number,
        'form':purchase_form
        }
    return render(request, 'purchase.html', context)

def dispatch(request, item):
    if item:
        product = Product.objects.get(id=item)
        stock_list=[]
        for x in range(1,product.stock+1):
            stock_list.append(x)
        context = {'product':product,'stock_list':stock_list}
        return render(request, 'dispatch.html', context)
    
def display_details(request, iid):
    p = Product.objects.get(id = iid)
    context = {'p':p}
    print(iid)
    return render(request, 'item_details.html', context)   

def update_product(request, pid):
    if pid:
        item = Product.objects.get(id=pid)
        cat = Category.objects.all()
        num_packet=[]
        for i in range(0,100):
            num_packet.append(i)
        context = {'item':item, 'cat':cat,'num_packet':num_packet}
        return render(request, 'includes/update_product.html', context)

def stock(request):
    product = Product.objects.select_related('category')
    p = Paginator(product, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    context = {'flag':3, 'page_obj':page_obj}
    if request.method == 'POST':
        search = request.POST['search']
        product = Product.objects.filter(Q(name__icontains=search) |  Q(description__icontains=search))
        context = {'flag':3, 'product':product}
        return render(request, 'stock.html', context)
    return render(request, 'stock.html', context)
def stockRoute(request, flag):
    flag = int(flag)
    context = {}
    if flag == 1:
        flag = flag
        total = Sale.objects.all().aggregate(Sum('total_profit'), Sum('total_price'))
        totalStock = Product.objects.all().aggregate(Sum('stock'))
        today = datetime.today()
        year = today.year
        month = today.month
        day = today.day
        today = Sale.objects.filter(date_created__year = year,date_created__month=month, date_created__day=day).aggregate(Sum('total_price'), Sum('total_profit'), Sum('quantity'))
        context = {'flag':flag, 'total':total, 'totalStock':totalStock, 'today':today}
    elif flag == 2:
        flag = flag
        context = {'flag':flag}
    elif flag == 3:
        product = Product.objects.select_related('category')
        p = Paginator(product, 6)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        flag = flag
        context = {'flag':flag, 'page_obj':page_obj}
        
    elif flag == 4:
        flag = flag
        return redirect("store:sale_info")
    return render(request, 'stock.html', context)

def update_stock(request):
    if request.method == 'POST':
        item_id = request.POST['item_id']
        new_stock = request.POST['new_stock']
        old = Product.objects.get(id = item_id)
        total_stock = int(old.stock) + int(new_stock)
        Product.objects.filter(id = item_id).update(stock = total_stock)
        messages.success(request,"The Stock Updated Successfully !")
        product = Product.objects.select_related('category')
    context = {'flag':3,'product':product}
    return render(request, 'stock.html', context)

def sale_search(request):
    if request.method == 'POST':
        search = request.POST['search']
        product = Product.objects.filter(Q(name__icontains=search) |  Q(description__icontains=search))
        context = {'product':product}
        return render(request, 'sales.html', context)
    
def addToCart(request):
    if request.method == 'POST':
        iid = request.POST['itemId']
        u = request.user.id
        #TRYING TO GET THE CUSTOMER CART START
        try:
            myCartId = Cart.objects.values_list('id', flat=True).get(customer = u)
            #TRYING TO CHECK WHETHER THE ITEM EXIST IN THE CART OR NOT START
            try:
                cartId = cartItem.objects.values_list('id', flat=True).get(product_id=iid)
                qty = cartItem.objects.values_list('quantity', flat=True).get(product_id=iid)
                qty += 1
                cartItem.objects.filter(id=cartId).update(quantity=qty)
                messages.success(request, "quantity updated")
            except cartItem.DoesNotExist:
                new_record = cartItem(product_id=iid, quantity=1, cart_id=myCartId)
                new_record.save()
                messages.success(request, "product added to cart")
            #TRYING TO CHECK WHETHER THE ITEM EXIST IN THE CART OR NOT END
        except Cart.DoesNotExist:
            obj = Cart(customer_id = u)
            obj.save()
            new_record = cartItem(product_id=iid, quantity=1, cart_id=obj.id)
            new_record.save()
            messages.success(request, "Product added to your cart successfully ! ")
        #TRYING TO GET THE CUSTOMER CART ENDS
        customer_cart = Cart.objects.values_list('id', flat=True).get(customer_id=u)
        cart_item = cartItem.objects.filter(cart_id=customer_cart).count()
        message = "success"
        status = 200
        data = {"message":message, "status":status, "cart_item":cart_item}
        return JsonResponse(data, safe=False)
    
def cart_item(request):
    cart_id = Cart.objects.values_list('id').get(customer_id = request.user.id)
    products=cartItem.objects.select_related('product').filter(cart_id=cart_id)
    context = {'products':products}
    return render(request, 'cart_item.html', context)

def update_quantity(request):
    if request.method =='POST':
        qty = request.POST['quantity']
        cartItemId = request.POST['cartItemId']
        cartItem.objects.filter(id=cartItemId).update(quantity=qty)
        
        data = {'quantity':qty, 'cart_item_id':cartItemId}
    return JsonResponse(data, safe=False)

def purchaseItem(request):
    user_id = request.user.id
    my_cart_id = Cart.objects.values_list('id', flat=True).get(customer_id=user_id)
    my_cart_item = cartItem.objects.select_related('product').filter(cart_id = my_cart_id)
    
    
    
    my_list=[]
    
    for val in my_cart_item:
        total_price = int(val.quantity) * int(val.product.price)
        profit=int(val.product.price) - int(val.product.rate)
        total_profit = profit * val.quantity
        stock = int(val.product.stock) - int(val.quantity)
        new_record=Sale(quantity=val.quantity, total_price=total_price,  total_profit=total_profit, cart_id=my_cart_id, product_id=val.product.id )
        new_record.save()
        my_list.append(new_record)
        Product.objects.filter(id=val.product.id).update(stock=stock)
        
    messages.success(request, "stock updated, Sale Table created")
    store_info = CustomUser.objects.select_related('store').get(id=user_id)
    print(store_info.store)
    payment = 0
    for  i in my_list:
        payment = payment + i.total_price
    context = {'sold_products': my_list,'store_info':store_info,'payment':payment}
    
    cartItem.objects.filter(cart_id = my_cart_id).delete()
    
    messages.success(request, "Your Cart item has been Removed")
    
    return render(request, 'sale_item.html', context)

def RemoveCartIem(request, pid):
    if pid:
        cartItem.objects.filter(id=pid).delete()
        cart_id = Cart.objects.values_list('id').get(customer_id = request.user.id)
    products=cartItem.objects.select_related('product').filter(cart_id=cart_id)
    context = {'products':products}
    return render(request, 'cart_item.html', context)

def purchaseSearch(request):
    goods = ''
    if request.method == 'POST':
        item = request.POST['search']
        product = Product.objects.filter(Q(name__icontains=item) |  Q(description__icontains=item))
        goods = product
        
    p = Paginator(goods, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
        
    context = {'page_obj':page_obj}
    return render(request, 'purchase.html', context)

def sale_info(request):
    if request.method == 'POST':
        date_from = request.POST['from']
        date_to = request.POST['to']
        product = Sale.objects.filter( date_created__range=(date_from, date_to))
        p = Paginator(product, 6)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        
        context = {'page_obj':page_obj}
        return render(request, 'includes/sale_info.html', context)
        
    product = Sale.objects.select_related('product').order_by('-date_created')
    p = Paginator(product, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    
    context = {'page_obj':page_obj}
    return render(request, 'includes/sale_info.html', context)

def getItemInfo(request):
    if request.method == 'POST':
        pid = request.POST['pid']
        productId = Sale.objects.values_list('product', flat=True).get(id=pid)
        productInfo = Product.objects.filter(id=productId).values()
        
        cartId = Sale.objects.values_list('cart', flat=True).get(id=pid)
        customer_id = Cart.objects.values_list('customer', flat=True).get(id=cartId)
       
        customer_info = CustomUser.objects.values().get(id=customer_id)
        print(customer_info)
        saleProduct = Sale.objects.select_related('product').filter(id = pid).values()
        data = {'saleProduct':list(saleProduct), 'customerInfo':customer_info, 'productInfo':list(productInfo)}
    
        return JsonResponse(data, safe=False)
    
def summeryByDate(request):
    if request.method == 'POST':
        date_to = request.POST['to']
        date_from = request.POST['from']
        
        filter_info = {
            'start_day' : date_from,
            'end_day' : date_to 
        }
        selectedData = Sale.objects.filter( date_created__range=(date_from, date_to)).aggregate(Sum('total_price'), Sum('total_profit'), Sum('quantity'))
        flag = 1
        total = Sale.objects.all().aggregate(Sum('total_profit'), Sum('total_price'))
        totalStock = Product.objects.all().aggregate(Sum('stock'))
        today = datetime.today()
        year = today.year
        month = today.month
        day = today.day
        today = Sale.objects.filter(date_created__year = year,date_created__month=month, date_created__day=day).aggregate(Sum('total_price'), Sum('total_profit'), Sum('quantity'))
        context = {'flag':flag, 'total':total, 'totalStock':totalStock, 'today':today, 'selectedData':selectedData,'filterInfo':filter_info}
        return render(request, 'stock.html', context)
    return redirect("store:stockRoute", 1)
    
def buyItem(request):
    if request.method == 'POST':
        item_id = request.POST['itemId']
        product = Product.objects.filter(id = item_id).values()
        data = {'product':list(product), 'Message': 'Success', 'status':200}
        return JsonResponse(data, safe=False)
        
def buyRoute(request, dataItem):
    print(dataItem)
    context = {'product':dataItem}
    return render(request, 'buy_item.html', context)   

def saleItem(request):
    if request.method == 'POST':
        pid = request.POST['pid']
        quantity = request.POST['qty']
        pro = Product.objects.get(id=pid)
        new_stock = int(pro.stock) - int(quantity)
        total_price = int(quantity) * int(pro.price)
        total_profit = int(quantity) * int(pro.profit)
        new_stock = int(pro.stock) - int(quantity)
        Product.objects.filter(id=pid).update(stock = new_stock)
        new_record = Sale(product_id=pid, quantity=quantity,total_price=total_price,total_profit=total_profit)
        new_record.save()
        messages.success(request, "Product sold successfully ")
        
        
        data = {'pid':pid,'qty':quantity}
        return JsonResponse(data, safe=False)
    

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        userDetails = CustomUser.objects.filter(email=email).values()
        # place the email code here
        
        num = random.randrange(0,1000000)
        data = {"status":200, 'otp':num, 'userDetail':list(userDetails)}
        return JsonResponse(data, safe=False)
    context = {}
    return render(request, 'forgot_password.html', context)
        
def verifyOtp(request):
    if request.method == 'POST':
        userOtp = request.POST['userOtp']
        sysOtp = request.POST['sysOtp']
        userId = request.POST['userId']
        if int(userOtp) == int(sysOtp):
            context={'userID':userId}
            return render(request, 'reset_password.html', context)
        else:
            messages.error(request, "The OTP is Invalid ! Please Try again...")
            return render(request, 'forgot_password', context)