from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *
import json
from django.http import JsonResponse
from .models import Booking
from django.db.models import Count
from django.utils import timezone
import datetime

# Create your views here.
def home(request):
    return render(request,'home.html')

def index(request):
    return render(request,'navbar.html')

def about(request):
    return render(request, 'about.html')


def main(request):
    data = Carousel.objects.all()
    dic = {'data':data}
    return render(request, 'index.html', dic)

def adminLogin(request):
    msg = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            if user.is_staff:
                login(request, user)
                msg = "User login successfully"
                return redirect('admindashboard')
            else:
                msg = "Invalid Credentials"
        except:
            msg = "Invalid Credentials"
    dic = {'msg': msg}
    return render(request, 'admin_login.html', dic)

def adminHome(request):
    return render(request, 'admin_base.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def add_category(request):
    if request.method == "POST":
        name = request.POST['name']
        Category.objects.create(name=name)
        msg = "Category added"
        return redirect('view_category')
    return render(request, 'add_category.html', locals())

def view_category(request):
    category = Category.objects.all()
    return render(request, 'view_category.html', locals())

def edit_category(request, pid):
    category = Category.objects.get(id=pid)
    if request.method == "POST":
        name = request.POST['name']
        category.name = name
        category.save()
        msg = "Category Updated"
        return redirect('view_category')
    return render(request, 'edit_category.html', locals())

def delete_category(request, pid):
    category = Category.objects.get(id=pid)
    category.delete()
    return redirect('view_category')

def add_product(request):
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        cat = request.POST['category']
        discount = request.POST['discount']
        desc = request.POST['desc']
        image = request.FILES['image']
        catobj = Category.objects.get(id=cat)
        Product.objects.create(name=name, price=price, discount=discount, category=catobj, description=desc, image=image)
        msg="Product added"
        return redirect("view_product")
    return render(request, 'add_product.html', locals())

def view_product(request):
    product = Product.objects.all()
    return render(request, 'view_product.html', locals())

def edit_product(request, pid):
    product = Product.objects.get(id=pid)
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        cat = request.POST['category']
        discount = request.POST['discount']
        desc = request.POST['desc']
        try:
            image = request.FILES['image']
            product.image = image
            product.save()
        except:
            pass
        catobj = Category.objects.get(id=cat)
        Product.objects.filter(id=pid).update(name=name, price=price, discount=discount, category=catobj, description=desc)
        msg="Product Updated"
    return render(request, 'edit_product.html', locals())


def delete_product(request, pid):
    product = Product.objects.get(id=pid)
    product.delete()
    msg="Product Deleted"
    return redirect('view_product')

def registration(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        address = request.POST['address']
        mobile = request.POST['mobile']
        user = User.objects.create_user(username=email, first_name=fname, last_name=lname, email=email, password=password)
        UserProfile.objects.create(user=user, mobile=mobile, address=address)
        msg="Registration Successful"
    return render(request, 'registration.html', locals())

def userlogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            msg ="User login successfully"
            return redirect('main')
        else:
           msg="Invalid Cnx"
    return render(request, 'userlogin.html', locals())

def logoutuser(request):
    logout(request)
    msg="Logout Successfully"
    return redirect('main')


def user_product(request,pid):
    if pid == 0:
        product = Product.objects.all()
    else:
        category = Category.objects.get(id=pid)
        product = Product.objects.filter(category=category)
    allcategory = Category.objects.all()
    return render(request, "user-product.html", locals())


def product_detail(request, pid):
    product = Product.objects.get(id=pid)
    latest_product = Product.objects.filter().exclude(id=pid).order_by('-id')[:10]
    return render(request, "product_detail.html", locals())

def addToCart(request, pid):
    myli = {"objects":[]}
    try:
        cart = Cart.objects.get(user=request.user)
        myli = json.loads((str(cart.product)).replace("'", '"'))
        try:
            myli['objects'][0][str(pid)] = myli['objects'][0].get(str(pid), 0) + 1
        except:
            myli['objects'].append({str(pid):1})
        cart.product = myli
        cart.save()
    except:
        myli['objects'].append({str(pid): 1})
        cart = Cart.objects.create(user=request.user, product=myli)
    return redirect('cart')


def incredecre(request, pid):
    cart = Cart.objects.get(user=request.user)
    if request.GET.get('action') == "incre":
        myli = json.loads((str(cart.product)).replace("'", '"'))
        myli['objects'][0][str(pid)] = myli['objects'][0].get(str(pid), 0) + 1
    if request.GET.get('action') == "decre":
        myli = json.loads((str(cart.product)).replace("'", '"'))
        if myli['objects'][0][str(pid)] == 1:
            del myli['objects'][0][str(pid)]
        else:
            myli['objects'][0][str(pid)] = myli['objects'][0].get(str(pid), 0) - 1
    cart.product = myli
    cart.save()
    return redirect('cart')


def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        product = (cart.product).replace("'", '"')
        myli = json.loads(str(product))
        product = myli['objects'][0]
    except:
        product = []
    lengthpro = len(product)
    return render(request, 'cart.html', locals())


def deletecart(request, pid):
    cart = Cart.objects.get(user=request.user)
    product = (cart.product).replace("'", '"')
    myli = json.loads(str(product))
    del myli['objects'][0][str(pid)]
    cart.product = myli
    cart.save()
    msg="Delete Successfully"
    return redirect('cart')

def booking(request):
    user = UserProfile.objects.get(user=request.user)
    cart = Cart.objects.get(user=request.user)
    total = 0
    productid = (cart.product).replace("'", '"')
    productid = json.loads(str(productid))
    try:
        productid = productid['objects'][0]
    except:
        msg="Cart is empty, Please add product in cart."
        return redirect('cart')
    for i,j in productid.items():
        product = Product.objects.get(id=i)
        total += int(j) * int(product.price)
    if request.method == "POST":
        book = Booking.objects.create(user=request.user, product=cart.product, total=total)
        cart.product = {'objects':[]}
        cart.save()
        msg = "Book Order Successfully"
        return redirect('main')
    return render(request, "booking.html", locals())

def myOrder(request):
    order = Booking.objects.filter(user=request.user)
    return render(request, "my-order.html", locals())

def manage_order(request):
    action = request.GET.get('action', 0)
    order = Booking.objects.filter(status=int(action))
    order_status = ORDERSTATUS[int(action)-1][1]
    if int(action) == 0:
        order = Booking.objects.filter()
        order_status = 'All'
    order_status_choices = ORDERSTATUS
    return render(request, 'manage_order.html', {'order': order, 'order_status': order_status, 'order_status_choices': order_status_choices})


def delete_order(request, pid):
    order = Booking.objects.get(id=pid)
    order.delete()
    msg='Order Deleted'
    return redirect('/manage-order/?action='+request.GET.get('action'))

def update_status(request, pid):
    if request.method == "POST":
        order = Booking.objects.get(id=pid)
        new_status = int(request.POST.get('status'))
        order.status = new_status
        order.save()
        return redirect(f'/manage-order/?action={request.GET.get("action", 0)}')

def manage_user(request):
    user = UserProfile.objects.all()
    return render(request, 'manage_user.html', locals()) 

def delete_user(request, pid):
    user = User.objects.get(id=pid)
    user.delete()
    msg="User deleted successfully"
    return redirect('manage_user') 

def admin_dashboard(request):
    user = UserProfile.objects.filter()
    product = Product.objects.filter()
    order = Booking.objects.filter()

    return render(request, 'admin_dashboard.html', locals())


def orders_chart_data(request):
    # Récupération des données de commande par jour pour les 7 derniers jours
    today = timezone.now().date()
    start_date = today - datetime.timedelta(days=6)  # Inclure aujourd'hui et les 6 jours précédents

    orders_by_day = Booking.objects.filter(created__date__range=[start_date, today]) \
        .extra({'day': "date(created)"}) \
        .values('day') \
        .annotate(count=Count('id')) \
        .order_by('day')

    # Générer une liste de jours de la semaine pour les 7 derniers jours
    labels = [(start_date + datetime.timedelta(days=i)).strftime('%A') for i in range(7)]
    data = [0] * 7  # Initialiser les données à 0 pour chaque jour

    print(f"Orders by day: {list(orders_by_day)}")  # Ajout de l'impression pour voir les commandes récupérées

    for order in orders_by_day:
        day_str = order['day']
        day = datetime.datetime.strptime(day_str, '%Y-%m-%d').date()
        print(f"Order day: {day}, Day index: {(day - start_date).days}")
        day_index = (day - start_date).days
        if 0 <= day_index < 7:
            data[day_index] = order['count']
    
    print(f"Labels: {labels}")
    print(f"Data: {data}")

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })





