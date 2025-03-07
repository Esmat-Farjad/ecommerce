from datetime import datetime
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import random
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import Category, CustomUser, Sale, Product
from .forms import ProductSearchForm, PurchaseProductForm, UpdateProductForm, UserCreationForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core import serializers


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
    request.breadcrums =[
        {"name":"home","url":"/"}
    ]
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
    grant_total = 0
    for product in products:
        quantity = cart[str(product.id)]
        total_price =quantity * int(product.price)
        grant_total= int(grant_total)+int(total_price)
        cart_item.append({'product':product,'quantity':quantity,'total':total_price})
    context = {
        'cart_item':cart_item,
        'num_item':len(cart_item),
        'grant_total':grant_total
    }
    return render(request,'cart_detail.html',context)

@login_required
def remove_cart_item(request, item):
    cart = request.session.get('cart',{})
    del cart[str(item)]
    request.session['cart']=cart
    return redirect('store:cart_detail')
@login_required
def change_quantity(request, pk, action):
    cart = request.session.get('cart',{})
    value = cart[str(pk)]
    if action == 'inc':
        value = int(value)+1
        cart[str(pk)] = value
    elif action == 'dec' and cart[str(pk)] > 1 :
        value = int(value) - 1
        cart[str(pk)] = value
    elif action == 'dec' and cart[str(pk)] == 1:
        del cart[str(pk)]
    
    request.session['cart']=cart
    return redirect('store:cart_detail')
@login_required
def sale_item(request):
    cart = request.session.get('cart', {})
    sales = []
    grant_total = 0
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            total_price = product.price * quantity
            total_profit= total_price - (quantity*product.rate)
            sales.append(Sale(product=product,quantity=quantity, total_price=total_price,total_profit=total_profit))
            old_stock = product.stock
            new_stock = old_stock - quantity
            grant_total = grant_total + total_price
            Product.objects.filter(id=product_id).update(stock=new_stock)
        except Product.DoseNotExist:
            continue
    Sale.objects.bulk_create(sales)
    request.session['cart']={}
    context = {
        'sold_products':sales,
        'grant_total':grant_total
    }
    return render(request, 'sale_page.html',context)

def signout(request):
    logout(request)
    messages.success(request, "You've been successfully logged out.")
    return render(request, 'home.html')

def product(request):
    product = Product.objects.all().order_by('-id')
    #Paginator start
    p = Paginator(product, 14)
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
            packet_contain = purchase_form.cleaned_data.get('packet_contain')
            num_packet = purchase_form.cleaned_data.get('num_packet')
            total_price = purchase_form.cleaned_data.get('bulk_price')
            rate  = round((total_price / packet_contain),3)
            profit = round((price - rate),3)
            stock = packet_contain * num_packet
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
    p = Paginator(product, 14 )
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

def manage_product(request, action, pid):
    product = get_object_or_404(Product, pk=pid)

    if pid and action == 'edit':
        form = UpdateProductForm(instance=product)
        if request.method == 'POST':
            form = UpdateProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
        context = {
            'product':product,
            'form':form
        }
        return render(request, 'includes/update_product.html', context)
    elif pid and action == 'delete':
        Product.objects.filter(id=pid).delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("store:product")

def stock(request):
    product = Product.objects.select_related('category')
    sale = Sale.objects.all().order_by('-quantity')
    # plotly gantt_chart
    total_income = sum(c.total_profit for c in sale)
    total_expense = sum(c.product.rate for c in sale)
    product_names = []
    product_profit = []
    for item in sale:
        product_names.append(item.product.name)  # Add product name to the names list
        product_profit.append(item.total_profit)   

    p = Paginator(sale, 8)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    fig = px.pie(
        values=product_profit,
        names=product_names
    )
    fig.update_layout(
        title_text="Total Profit per Products sold",
        width=500
    )
    
    fig.update_traces(
    hovertemplate='<b>Product name: %{label}</b><br>Profit: $%{value}<extra></extra>'
    )
    fig2 = px.bar(
        x=[item.product.name for item in sale],
        y=[item.quantity for item in sale],
    )
    fig2.update_layout(
        title_text="Products per quantity sold",
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis_title="Product Names",
        yaxis_title="Quantity Sold",
        plot_bgcolor="skyblue",  # Background color for the plot area
        paper_bgcolor="white",
        xaxis_tickangle=45,  # Rotate x-axis labels by 45 degrees for readability
        yaxis_tickformat=",.0f",
        hovermode='closest',
        width=500,
        
    )
    fig2.update_traces(marker=dict(color="#a52824"))
    context = {
        'flag':3, 
        'page_obj':page_obj,
        'chart':fig.to_html(),
        "lineChart":fig2.to_html(),
        "total_income":total_income,
        "total_expense":total_expense
        }
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



def search_product(request):
    if request.method == 'POST':
        data = request.POST.get("search-input")
        if data:
        # Access the data
            product_list = Product.objects.filter(name__startswith=data)
        else:
            product_list = Product.objects.none()
        context = {
            "items":product_list
        }
        return render(request, "_option_form.html", context)

        

