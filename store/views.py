from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Category, CustomUser, Store, Product
from .forms import UserCreationForm,StoreCreationForm
from django.db.models import Q


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
    product = Product.objects.select_related('category')
    context = {'product':product}
    return render(request, 'sales.html',context)

def signout(request):
    logout(request)
    return render(request, 'signin.html')

def product(request):
    if request.method == 'POST':
        id = request.POST['getid']
        Product.objects.filter(id=id).delete()
        messages.success(request, "Item Deleted Successfully !")
    product = Product.objects.all().order_by('-id')
    context = {'product':product,'flag':'list'}
    return render(request, 'product.html', context)


def purchase(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        category = request.POST['category']
        price = request.POST['price']
        bulk_price = request.POST['bprice']
        mfd = request.POST['mfd']
        expd = request.POST['expd']
        packet = request.POST['packet_content']
        item_pics=request.FILES['item_pics']
        num_packet = request.POST['num_packet']
        quantity = int(packet) * int(num_packet) 
        rate = round(int(bulk_price)/int(quantity), 2)
        profit = int(price) - int(rate)
        stock = quantity
        print(rate,profit,stock)
        # if category == 3 :
        new_record = Product(name=name, description=description,category_id=category,price=price,bulk_price=bulk_price,quantity=quantity,rate=rate,mfd=mfd,expd=expd,profit=profit,stock=stock, packet=packet, image=item_pics)
        # else:
            # new_record = Product(name=name, description=description,category_id=category,price=price,bulk_price=bulk_price,quantity=quantity,rate=rate,profit=profit,stock=stock, packet=packet, image=item_pics)
            
        new_record.save()
        messages.success(request, "Product added successfully !")
    product = Product.objects.all().order_by('-id')
    number = []
    for x in range(1, 100,1):
        number.append(x)
    cat = Category.objects.all()
    context = {'category':cat,'product':product,'num':number}
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
    context = {'flag':3, 'product':product}
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
        context = {'flag':flag}
    elif flag == 2:
        flag = flag
        context = {'flag':flag}
    elif flag == 3:
        product = Product.objects.select_related('category')
        flag = flag
        context = {'flag':flag, 'product':product}
    elif flag == 4:
        flag = flag
        context = {'flag':flag}
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