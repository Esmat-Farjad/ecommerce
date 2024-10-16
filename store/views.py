from datetime import datetime

import math

import random
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import Category, CustomUser, Sale, Product
from .forms import ProductSearchForm, PurchaseProductForm, UserCreationForm
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
    product_list = Product.objects.all().order_by('-id')
    search_form = ProductSearchForm()
    if 'query' in request.GET:
        search_form = ProductSearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            product_list = Product.objects.filter(name__icontains=query)

    # setting up paginator
    p = Paginator(product_list, 14)
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
    cart_length = 0
    if request.session.get('cart',{}):
        cart = request.session.get('cart',{})
        cart_length = len(cart)
    context = {
        'page_obj':page_obj,
        'search_form':search_form,
        'num_item':cart_length
        }
    
    return render(request, 'sales.html',context)


@login_required
def add_to_card(request,pid):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=pid)
        cart = request.session.get('cart',{})
        if str(product.id) in cart:
            cart[str(product.id)]  += 1
        else:
            cart[str(product.id)] = 1
        request.session['cart'] = cart
        
        data = {'cart':cart,'num_item':len(cart)}
        return JsonResponse(data, safe=False)

def cart_detail(request):
    cart = request.session.get('cart',{})
    products = Product.objects.filter(id__in=cart.keys())
    cart_item = []
    for product in products:
        quantity = cart[str(product.id)]
        total_price =quantity * int(product.price)
        cart_item.append({'product':product,'quantity':quantity,'total':total_price})
    context = {
        'cart_item':cart_item,
        'num_item':len(cart_item)
    }
    return render(request,'cart_detail.html',context)

@login_required
def remove_cart_item(request, item):
    cart = request.session.get('cart',{})
    if item in cart:
        value = cart.pop(cart[str(item)],None)
        request.session['cart'] = cart
        messages.success(request, f"{value} removed successfully !")
    else:
        messages.error(request,f"{cart[str(item)]} item not found")
    
    
    return redirect('store:cart_detail')

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