from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Category, CustomUser, Store, Product
from .forms import UserCreationForm,StoreCreationForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'main/base.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'your account has been created successfully !')
        else:
            messages.error(request, 'Oops...Something went wrong. Try again')
    form = UserCreationForm()
    context = {'form':form}
    return render(request, 'signup.html', context)
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('store:sales')
        else:
            messages.error(request, 'The username or password is incorrect !')

    context= {}
    return render(request, 'signin.html', context)

def sales(request):
    if request.method == 'POST':
        form = StoreCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'The Store added Successfully')
            
    form = StoreCreationForm()
    context = {'form':form}
    return render(request, 'sales.html',context)

def signout(request):
    logout(request)
    return render(request, 'signin.html')

def product(request):
    
    context = {'flag':'list'}
    return render(request, 'product.html', context)

def routeProduct(request, flag):
    if flag == 'list':
        sign = flag
        context = {'flag':sign}
    elif flag == 'add':
        sign = flag
        context = {'flag':sign}
    elif flag == 'update':
        sign = flag
        context = {'flag':sign}
    elif flag =='delete':
        sign = flag
        context = {'flag':sign}
    return render(request, 'product.html', context)

def purchase(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        category = request.POST['category']
        price = request.POST['price']
        bulk_price = request.POST['bprice']
        quantity = request.POST['quantity']
        mfd = request.POST['mfd']
        expd = request.POST['expd']
        rate = round(int(bulk_price)/int(quantity), 2)
        profit = int(price) - int(rate)
        stock = quantity
        print(rate,profit,stock)
        new_record = Product(name=name, description=description,category_id=category,price=price,bulk_price=bulk_price,quantity=quantity,rate=rate,mfd=mfd,expd=expd,profit=profit,stock=stock)
        new_record.save()
        messages.success(request, "Product added successfully !")
    product = Product.objects.all().order_by('-id')
    cat = Category.objects.all()
    context = {'category':cat,'product':product}
    return render(request, 'purchase.html', context)