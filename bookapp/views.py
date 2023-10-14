from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader, Template
from django.middleware.csrf import get_token
from bookapp.models import users, Listings, order, purchased_books
from bookapp.bookapis import get_book_info_from_isbn
import smtplib
import random
import string
import time
import calendar
from datetime import datetime
import json
import ast

# import custom functions

# Create your views here.

# Homepage
def homepage(request):
    csrf_token = get_token(request)

    #sorts the listings based on most viewed and selects the top 7 to be displayed (can be changed)
    listings = Listings.objects.all().order_by('-times_viewed').values()
    number_of_best_selling = 7
    listings = listings[:number_of_best_selling]
    '''print(listings)
    listings = Listings.objects.filter(id=-1).values()
    number_of_best_selling = 7  # number of listings shown on homepage
    # show only the first ____ number of listings
    for i in range(number_of_best_selling):
        checkid = str(i+1)
        listings = listings | Listings.objects.filter(id=checkid).values()
        # print(len(listings))'''
    if 'user_login' in request.session:
        name = users.objects.get(id=request.session['user_login']).firstname
        context = {
            "csrf_token": csrf_token,
            "home_class": "active",
            "about_class": "inactive",
            "contact_class": "inactive",
            "ishidden": "hidden",
            "isnothidden": "",
            "listings": listings,
            "name": name,
        }
    else:
        context = {
            "csrf_token": csrf_token,
            "home_class": "active",
            "about_class": "inactive",
            "contact_class": "inactive",
            "ishidden": "",
            "isnothidden": "hidden",
            "listings": listings,
        }

    renderdata = {}
    renderdata['context'] = context
    template = loader.get_template('homepage.html')
    return HttpResponse(template.render(renderdata, request))


def signup(request):
    if 'user_login' in request.session:
        return redirect('homepage')
    else:
        # Create csrf token
        csrf_token = get_token(request)

        # If the form is submitted
        if request.method == "POST":
            # check if email id does not already exist
            if not users.objects.filter(email_id=request.POST["email"]):
                # check if passwords match or not
                error_message = ""
                context = {
                    "csrf_token": csrf_token,
                    "error_message": error_message,
                    "ishidden": "",                        "isnothidden": "hidden"
                }
                user_id = ''.join(random.choices(string.digits, k=18))
                firstname = request.POST["firstname"]
                lastname = request.POST["lastname"]
                emailid = request.POST["email"]
                pw = request.POST["password_1"]
                otp = ''.join(random.choices(string.digits, k=6))
                request.session['user_verify'] = [user_id, firstname, lastname, emailid, pw, otp]
                request.session.modify = True
                with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()

                    smtp.login('ispsinstock@gmail.com', 'acsfrsxmxbtcrmbj')

                    subject = 'Reprose email verification'
                    body = f'To verify your email, enter the following OTP where indicated. Do not send this OTP to anyone \n {otp}'

                    msg = f'Subject: {subject}\n\n{body}'

                    smtp.sendmail('ispsinstock@gmail.com',
                                  emailid, msg)
                return redirect('verification')
            else:
                error_message = "Email ID is already registered"
                context = {
                    "csrf_token": csrf_token,
                    "error_message": error_message,
                    "ishidden": "",
                    "isnothidden": "hidden"
                }
                template = loader.get_template('signup.html')
                renderdata = {}
                renderdata['context'] = context
                return HttpResponse(template.render(renderdata, request))
        else:
            context = {
                "csrf_token": csrf_token,
                "ishidden": "",
                "isnothidden": "hidden"
            }
            renderdata = {}
            renderdata['context'] = context
            template = loader.get_template('signup.html')
            return HttpResponse(template.render(renderdata, request))

def verification(request):
    if 'user_verify' in request.session:
        csrf_token = get_token(request)
        context = {
            "csrf_token": csrf_token,
        }
        print(request.session['user_verify'])
        if request.method == "POST":
            otp = request.POST['otp1'] + request.POST['otp2'] + request.POST['otp3'] + request.POST['otp4'] + request.POST['otp5'] + request.POST['otp6']
            if request.session['user_verify'][5] == otp:
                request.session['user_login'] = request.session['user_verify'][0]
                request.session.modify = True
                data = users(id=request.session['user_verify'][0], firstname=request.session['user_verify'][1], lastname=request.session['user_verify'][2], email_id=request.session['user_verify'][3], password=request.session['user_verify'][4])
                data.save()
                del request.session['user_verify']
                return redirect('homepage')
            else:
                context["error_message"] = "incorrect otp"
                template = loader.get_template('verification.html')
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('verification.html')
            return HttpResponse(template.render(context, request))
    else:
        return redirect('homepage')

def login(request):
    if 'user_login' in request.session:
        return redirect('homepage')
    else:
        # Create csrf token
        csrf_token = get_token(request)

        # Once form is submitted
        if request.method == "POST":
            email_address = request.POST["email"]
            pw = request.POST["password"]
            # Check if the particular email id and password exits in the database
            if users.objects.filter(email_id=email_address) and users.objects.filter(password=pw):
                user_id = users.objects.get(email_id=email_address).id
                if pw == users.objects.get(id=user_id).password:
                    error_message = ""
                    context = {
                        "csrf_token": csrf_token,
                        "error_message": error_message,
                        "ishidden": "",
                        "isnothidden": "hidden"
                    }
                    request.session['user_login'] = str(
                        users.objects.get(email_id=email_address).id)
                    request.session.modify = True
                    return redirect('homepage')
                else:
                    error_message = "record not found"
                    context = {
                        "csrf_token": csrf_token,
                        "error_message": error_message,
                        "ishidden": "",
                        "isnothidden": "hidden"
                    }

                    renderdata = {}
                    renderdata['context'] = context

                    template = loader.get_template('login.html')
                    return HttpResponse(template.render(renderdata, request))
            else:
                error_message = "record not found"
                context = {
                    "csrf_token": csrf_token,
                    "error_message": error_message,
                    "ishidden": "",
                    "isnothidden": "hidden"
                }
                renderdata = {}
                renderdata['context'] = context

                template = loader.get_template('login.html')
                return HttpResponse(template.render(renderdata, request))
        else:
            context = {
                "csrf_token": csrf_token,
                "ishidden": "",
                "isnothidden": "hidden"
            }

            renderdata = {}
            renderdata['context'] = context

            template = loader.get_template('login.html')
            return HttpResponse(template.render(renderdata, request))


def about(request):
    csrf_token = get_token(request)

    if 'user_login' in request.session:

        name = users.objects.get(id=request.session['user_login']).firstname

        context = {
            "csrf_token": csrf_token,
            "ishidden": "hidden",
            "isnothidden": "",
            "home_class": "inactive",
            "about_class": "active",
            "contact_class": "inactive",
            "name": name,
        }
    else:
        context = {
            "csrf_token": csrf_token,
            "ishidden": "",
            "isnothidden": "hidden",
            "home_class": "inactive",
            "about_class": "active",
            "contact_class": "inactive",
        }

    renderdata = {}
    renderdata['context'] = context
    template = loader.get_template('about.html')
    return HttpResponse(template.render(renderdata, request))


def contact(request):
    csrf_token = get_token(request)

    if request.method == "POST":
        if 'user_login' in request.session:
            email_address = users.objects.get(
                id=request.session['user_login']).email_id

            name = users.objects.get(
                id=request.session['user_login']).firstname

            context = {
                "csrf_token": csrf_token,
                "ishidden": "hidden",
                "isnothidden": "",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "active",
                "logged_in": True,
                "name": name,
            }
        else:
            email_address = request.POST["email"]

            context = {
                "csrf_token": csrf_token,
                "ishidden": "",
                "isnothidden": "hidden",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "active",
                "logged_in": False,
            }

        t = time.localtime()

        send_to = 'praneeth.suresh@giis.edu.sg'

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login('ispsinstock@gmail.com', 'acsfrsxmxbtcrmbj')

            message = f"""Dear manager,
            User with the email id {email_address} has the following query for you:

            {request.POST["query"]}

            The query was generated at {time.strftime("%H:%M:%S", t)}

            With Regards,
            Computer system
            """

            subject = 'Query for reprose'

            msg = f'Subject: {subject}\n\n{message}'

            smtp.sendmail('ispsinstock@gmail.com',
                          send_to, msg)

            print("Query send to manager.")

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login('reprose.xx@gmail.com', 'Garlicbread123')

            message = f"""Dear manager,
            User with the email id {email_address} has the following query for you:

            {request.POST["query"]}

            The query was generated at {time.strftime("%H:%M:%S", t)}

            With Regards,
            Computer system
            """

            subject = 'Query for reprose'

            msg = f'Subject: {subject}\n\n{message}'

            smtp.sendmail('reprose.xx@gmail.com',
                          send_to, msg)

            print("Query send to manager.")

    else:
        if 'user_login' in request.session:

            name = users.objects.get(
                id=request.session['user_login']).firstname

            context = {
                "csrf_token": csrf_token,
                "ishidden": "hidden",
                "isnothidden": "",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "active",
                "logged_in": True,
                "name": name,
            }
        else:
            context = {
                "csrf_token": csrf_token,
                "ishidden": "",
                "isnothidden": "hidden",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "active",
                "logged_in": False,
            }

    renderdata = {}
    renderdata['context'] = context
    template = loader.get_template('contact.html')
    return HttpResponse(template.render(renderdata, request))


def test(request):
    template = loader.get_template('test.html')
    return HttpResponse(template.render())


def profile(request):
    if 'user_login' in request.session:
        if request.POST.get('saveBtn') == "save":
            userdata = users.objects.get(id=request.session['user_login'])
            userdata.firstname = request.POST['firstname']
            userdata.lastname = request.POST['lastname']
            userdata.email_id = request.POST['email']
            userdata.password = request.POST['password']
            userdata.address = request.POST['address']
            userdata.save()

        UserBio = users.objects.get(
            id=request.session['user_login'])

        listings = Listings.objects.filter(userid=UserBio.id).values()

        listings = list(listings)

        context = {
            "ishidden": "hidden",
            "isnothidden": "",
            "home_class": "inactive",
            "about_class": "inactive",
            "contact_class": "inactive",
            "name": UserBio.firstname + " " + UserBio.lastname,
            "email": UserBio.email_id,
            "listings": listings,
            "num_listings": len(listings),
        }
        renderdata = {
            "context": context,
            "UserBio": UserBio,
        }
        template = loader.get_template('profile.html')
        return HttpResponse(template.render(renderdata, request))
    else:
        return redirect('login')

def order_history(request):
    user_orders = order.objects.filter(userid=request.session['user_login']).order_by('-timestamp')[:10]
    orderids = []
    prices = []
    timestamps = []
    datetimes = []
    for x in user_orders:
        orderids.append(x.id)
        prices.append(x.order_cost)
        timestamps.append(x.timestamp)
    for timestamp in timestamps:
        dt_object = datetime.utcfromtimestamp(timestamp)
        month = dt_object.strftime("%B")
        day = dt_object.day
        year = dt_object.year
        datetimes.append(f"{month} {day} {year}")
    listings = []
    for single_order in user_orders:
        x = single_order.order_cart
        book_ids = x.values()
        listings.append(Listings.objects.filter(id__in=book_ids))
    alldata = zip(listings, orderids, prices, datetimes)
    context = {
        "ishidden": "hidden",
        "isnothidden": "",
    }
    renderdata = {
        "context": context,
        "alldata": alldata,
        "prices": prices,
        "orderids": orderids,
        "user_orders": user_orders,
        "listings": listings,
    }
    template = loader.get_template('order_history.html')
    return HttpResponse(template.render(renderdata, request))

def payment_methods(request):
    template = loader.get_template('payment_methods.html')
    return HttpResponse(template.render())

def subscriptions(request):
    template = loader.get_template('subscriptions.html')
    return HttpResponse(template.render())

def profile_listings(request):
    if 'user_login' in request.session:
        print("listings profile")
        UserBio = users.objects.get(
            id=request.session['user_login'])

        listings = Listings.objects.filter(userid=UserBio.id).values()

        listings = list(listings)

        context = {
            "ishidden": "hidden",
            "isnothidden": "",
            "home_class": "inactive",
            "about_class": "inactive",
            "contact_class": "inactive",
            "name": UserBio.firstname + " " + UserBio.lastname,
            "email": UserBio.email_id,
            "listings": listings,
            "num_listings": len(listings)
        }
        renderdata = {}
        renderdata['context'] = context
        template = loader.get_template('profile_listings.html')
        return HttpResponse(template.render(renderdata, request))
    else:
        return redirect('login')


def browse_listings(request):
    csrf_token = get_token(request)
    listings = Listings.objects.all().values()
    if request.method == "POST":
        if request.POST.get('filter_search'):
            print("filter")
            query = "found"
            if request.POST.get('minprice'):
                min_price = request.POST.get('minprice')
            else:
                min_price = 0

            if request.POST.get('maxprice'):
                max_price = request.POST.get('maxprice')
            else:
                max_price = 1000

            if request.POST.get('condition'):
                condition = request.POST.get('condition')
            else:
                condition = "w"

            if request.POST.get('genre'):
                genre = request.POST.get('genre')
            else:
                genre = ""
            if request.POST.get('age_group'):
                age_group = request.POST.get('age_group')
            else:
                age_group = "1"
            if request.POST.get('saleLend'):
                saleLend = request.POST.get('saleLend')
            else:
                saleLend = "ing"
            listings = Listings.objects.filter(
                price__range=(min_price, max_price), condition__icontains=condition, saleOrBorrow__icontains=saleLend, age_group__icontains=age_group)
        else:
            print("no-filter")
            query = request.POST.get("query")
            listings = Listings.objects.filter(
                book_title__icontains=query) | Listings.objects.filter(description__icontains=query)
            query = "for " + request.POST.get("query")
        numberOfResults = listings.count()
        if listings:
            noResults = "hidden"
        else:
            noResults = ""
        if numberOfResults == 1:
            s = ""
        else:
            s = "s"
        if 'user_login' in request.session:

            name = users.objects.get(
                id=request.session['user_login']).firstname

            context = {
                "csrf_token": csrf_token,
                "ishidden": "hidden",
                "isnothidden": "",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "inactive",
                "query": query,
                "madequery": "",
                "listings": listings,
                "noResults": noResults,
                "numberOfResults": numberOfResults,
                "s": s,
                "name": name,
            }
        else:
            context = {
                "csrf_token": csrf_token,
                "ishidden": "",
                "isnothidden": "hidden",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "inactive",
                "query": query,
                "madequery": "",
                "listings": listings,
                "noResults": noResults,
                "numberOfResults": numberOfResults,
                "s": s,
            }
    else:
        noResults = "hidden"
        numberOfResults = 0
        s = ""
        if 'user_login' in request.session:

            name = users.objects.get(
                id=request.session['user_login']).firstname

            context = {
                "csrf_token": csrf_token,
                "ishidden": "hidden",
                "isnothidden": "",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "inactive",
                "query": "",
                "madequery": "hidden",
                "listings": listings,
                "noResults": noResults,
                "numberOfResults": numberOfResults,
                "s": s,
                "name": name,
            }
        else:
            context = {
                "csrf_token": csrf_token,
                "ishidden": "",
                "isnothidden": "hidden",
                "home_class": "inactive",
                "about_class": "inactive",
                "contact_class": "inactive",
                "query": "",
                "madequery": "hidden",
                "listings": listings,
                "noResults": noResults,
                "numberOfResults": numberOfResults,
                "s": s,
            }
    renderdata = {}

    renderdata['context'] = context
    template = loader.get_template('search.html')
    return HttpResponse(template.render(renderdata, request))


# add context and listings into a 2d dict called renderdata


def add_listing(request):
    csrf_token = get_token(request)
    if 'user_login' in request.session:

        name = users.objects.get(id=request.session['user_login']).firstname

        context = {
            "ishidden": "hidden",
            "isnothidden": "",
            "home_class": "inactive",
            "about_class": "inactive",
            "contact_class": "inactive",
            "csrf_token": csrf_token,
            "name": name,
        }
        if request.method == "POST":

            isbn = request.POST["isbn"].replace("-","")

            bookdata = get_book_info_from_isbn(isbn)
            book_title = bookdata[0]
            genre = bookdata[2][0]
            if bookdata[4] == 'NOT_MATURE':
                age = 18
            else:
                age = 13
            imgurl = bookdata[5]
            description = bookdata[1]
            saleOrBorrow = request.POST["listingType"]
            price = request.POST["price"]
            condition = request.POST['condition']
            try:
                data = Listings(userid=request.session['user_login'], book_title=book_title, isbn=isbn,
                                genre=genre, age_group=age, saleOrBorrow=saleOrBorrow, price=price, imgurl=imgurl, description=description, condition=condition, times_viewed=0, borrowed_date=0)
                data.save()
            except ValueError:
                price = 0
                data = Listings(userid=request.session['user_login'], book_title=book_title, isbn=isbn,
                                genre=genre, age_group=age, saleOrBorrow=saleOrBorrow, price=price, imgurl=imgurl, description=description, condition=condition, times_viewed=0, borrowed_date=0)
                data.save()
            return redirect('search')
        else:
            renderdata = {}
            renderdata['context'] = context
            template = loader.get_template('add_listing.html')
            return HttpResponse(template.render(renderdata, request))
    else:
        return redirect('login')


def remove_listing(request):
    bookid = request.POST['remove_listing']
    listings = Listings.objects.get(id=bookid)
    listings.delete()
    return redirect('profile_listings')


def signout(request):
    del request.session['user_login']
    return redirect('homepage')


def forgot(request):
    if 'user_login' in request.session:
        return redirect('homepage')
    else:
        # Create csrf token
        csrf_token = get_token(request)

        # Once form is submitted
        if request.method == "POST":
            if 'user_requested_password' in request.session:
                del request.session['user_requested_password']
            user_email_address = request.POST["email"]
            if users.objects.filter(email_id=user_email_address):
                context = {
                    "csrf_token": csrf_token,
                    "ishidden": "",
                    "isnothidden": "hidden",
                    "error_message": "",
                    "hide": "hidden",
                    "unhide": "",
                }
                renderdata = {}
                renderdata['context'] = context
                # generate random url extension
                url_extension = ''.join(random.choices(
                    string.ascii_lowercase + string.ascii_uppercase + string.digits, k=16))

                # Needs to send email with new password
                print("email address: ", user_email_address)

                # send email to reset password
                with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()

                    smtp.login('ispsinstock@gmail.com', 'acsfrsxmxbtcrmbj')

                    subject = 'Reprose Password Reset'
                    body = f'To reset your password, click on the following link: http://localhost:8000/resetPassword/{url_extension}'

                    msg = f'Subject: {subject}\n\n{body}'

                    smtp.sendmail('ispsinstock@gmail.com',
                                  user_email_address, msg)
                request.session['user_requested_password'] = [users.objects.get(
                    email_id=user_email_address).id]
                request.session['user_requested_password'].insert(
                    1, url_extension)
                template = loader.get_template('forgotPassword.html')
                return HttpResponse(template.render(renderdata, request))
            else:
                context = {
                    "csrf_token": csrf_token,
                    "ishidden": "",
                    "isnothidden": "hidden",
                    "error_message": "email id not found",
                    "hide": "",
                    "unhide": "hidden",
                }
                renderdata = {}
                renderdata['context'] = context
                template = loader.get_template('forgotPassword.html')
                return HttpResponse(template.render(renderdata, request))
        else:
            context = {
                "csrf_token": csrf_token,
                "ishidden": "",
                "isnothidden": "hidden",
                "error_message": "",
                "hide": "",
                "unhide": "hidden",
            }

            renderdata = {}
            renderdata['context'] = context

            template = loader.get_template('forgotPassword.html')
            return HttpResponse(template.render(renderdata, request))


def resetpw(request, extension):
    if 'user_login' in request.session:
        return redirect('homepage')
    elif 'user_requested_password' in request.session:
        if extension == request.session['user_requested_password'][1]:
            print(extension)
            print(request.session['user_requested_password'])
            csrf_token = get_token(request)
            if request.method == "POST":
                if request.POST['password1'] == request.POST['password2']:
                    context = {
                        "csrf_token": csrf_token,
                        "ishidden": "",
                        "isnothidden": "hidden",
                        "error_message": ""
                    }
                    renderdata = {}
                    renderdata['context'] = context
                    newpassword = request.POST['password1']
                    x = users.objects.get(
                        id=request.session['user_requested_password'][0])
                    x.password = newpassword
                    x.save()
                    request.session['user_login'] = request.session['user_requested_password'][0]
                    request.session.modify = True
                    print('deleting')
                    del request.session['user_requested_password']
                    print(request.session['user_login'])
                    return redirect('homepage')
                else:
                    context = {
                        "csrf_token": csrf_token,
                        "ishidden": "",
                        "isnothidden": "hidden",
                        "error_message": "passwords do not match"
                    }
                    renderdata = {}
                    renderdata['context'] = context
                    template = loader.get_template('resetPassword.html')
                    return HttpResponse(template.render(renderdata, request))
            else:
                context = {
                    "csrf_token": csrf_token,
                    "ishidden": "",
                    "isnothidden": "hidden",
                    "error_message": "",
                }
                renderdata = {}
                renderdata['context'] = context
                template = loader.get_template('resetPassword.html')
                return HttpResponse(template.render(renderdata, request))
        else:
            print('wrong extension')
            return redirect('forgotPassword')
    else:
        print('not in session')
        return redirect('forgotPassword')


def bookinfo(request, id):
    if 'may_add_to_cart' in request.session:
        del request.session['may_add_to_cart']
    bookdata = Listings.objects.filter(id=id).values()
    times_viewed = Listings.objects.get(id=id)
    times_viewed.times_viewed = times_viewed.times_viewed + 1
    times_viewed.save()
    if 'user_login' in request.session:
        name = users.objects.get(id=request.session['user_login']).firstname
        context = {
            "ishidden": "hidden",
            "isnothidden": "",
            "home_class": "inactive",
            "about_class": "inactive",
            "contact_class": "active",
            'id': id,
            "name": name,
        }
    else:
        context = {
            "ishidden": "",
            "isnothidden": "hidden",
            "home_class": "inactive",
            "about_class": "inactive",
            "contact_class": "active",
            'id': id,
        }
    renderdata = {
        "context": context,
        "bookdata": bookdata.values()[0],
    }
    request.session['may_add_to_cart'] = id
    template = loader.get_template('bookinfo.html')
    return HttpResponse(template.render(renderdata, request))
    #return HttpResponse('<p>The id is {}</p>'.format(id))


def cart(request):
    if 'user_login' in request.session:
        name = users.objects.get(id=request.session['user_login']).firstname
        print(users.objects.get(
                id=request.session['user_login']).cart)
        if request.method == "POST":
            if request.POST.get('addToCart_button') or request.POST.get('addFromBookPage'):
                print("first", request.POST.get('addToCart_button'))
                print("second", request.POST.get('addFromBookPage'))
                if request.POST.get('addToCart_button'):
                    cart_item = request.POST['addToCart_button']
                else:
                    cart_item = request.POST['addFromBookPage']
                isAlrInCart = False
                userdata = users.objects.get(
                    id=request.session['user_login']).cart
                print("users cart: ", userdata)
                if userdata == {}:
                    current_cart = userdata
                else:
                    current_cart = json.loads(userdata)
                for item in current_cart:
                    if current_cart[item] == cart_item:
                        isAlrInCart = True
                if not isAlrInCart:
                    if str(Listings.objects.get(id=cart_item).userid) == request.session['user_login']:
                        context = {
                            "ishidden": "hidden",
                            "isnothidden": "",
                            "error_message": "You cannot purchase an item that you have listed, please contact us if there has been a mistake",
                            "name": name,
                        }
                    else:
                        current_time = time.gmtime()
                        timestamp = calendar.timegm(current_time)
                        current_cart[timestamp] = cart_item
                        data = users.objects.get(id=request.session['user_login'])
                        data.cart = json.dumps(current_cart)
                        data.save()
                        print("users updated cart:", data)
                        context = {
                            "ishidden": "hidden",
                            "isnothidden": "",
                            "error_message": "",
                            "name": name,
                        }
                else:
                    context = {
                        "ishidden": "hidden",
                        "isnothidden": "",
                        "error_message": "Item has already been added to cart",
                        "name": name,
                    }
            elif request.POST.get('delete_button'):
                delete_item = request.POST['delete_button']
                userdata = users.objects.get(
                    id=request.session['user_login']).cart
                current_cart = json.loads(userdata)
                keys_with_value = [
                    key for key, value in current_cart.items() if value == delete_item]
                print("item to be deleted:", keys_with_value)
                context = {
                    "ishidden": "hidden",
                    "isnothidden": "",
                    "error_message": "",
                    "name": name,
                }
                print("deleting bookid:", current_cart[keys_with_value[0]])
                del current_cart[keys_with_value[0]]
                data = users.objects.get(id=request.session['user_login'])
                data.cart = json.dumps(current_cart)
                data.save()
                print(data)
        elif 'empty_cart' in request.session:
            context = {
                "ishidden": "hidden",
                "isnothidden": "",
                "error_message": request.session['empty_cart'],
                "name": name,
            }
            del request.session['empty_cart']
        else:
            context = {
                "ishidden": "hidden",
                "isnothidden": "",
                "error_message": "",
                "name": name,
            }
        if users.objects.get(id=request.session['user_login']).cart == {}:
            cart = users.objects.get(id=request.session['user_login']).cart
        else:
            cart = json.loads(users.objects.get(
                id=request.session['user_login']).cart)
        book_ids = list(cart.values())
        print("books in user's cart: ", book_ids)
        listings = Listings.objects.filter(id__in=book_ids)
        renderdata = {
            "context": context,
            "listings": listings,
            "userid": request.session['user_login'],
            "name": name,
        }
        renderdata['context'] = context
        template = loader.get_template('cart.html')
        return HttpResponse(template.render(renderdata, request))
    else:
        return redirect('login')


def checkout(request, userid):
    print(users.objects.get(id=userid).cart)
    if 'user_login' in request.session:
        if users.objects.get(id=userid).cart == "{}" or users.objects.get(id=userid).cart == {}:
            print(users.objects.get(id=userid).cart)
            request.session['empty_cart'] = "Cart is empty. Please add items to proceed to checkout"
            return redirect('cart')
        else:
            if str(request.session['user_login']) == userid:
                if request.method == "POST":
                    id = ''.join(random.choices(
                        string.ascii_lowercase + string.ascii_uppercase + string.digits, k=16))
                    firstname = request.POST['firstname']
                    lastname = request.POST['lastname']
                    email = request.POST['email']
                    company = request.POST.get('company')
                    address = request.POST['address1'] + " " + request.POST.get('address2') + " " + request.POST.get('address3')
                    city = request.POST['city']
                    zipcode = request.POST['zipcode']
                    userdata = users.objects.get(id=userid)
                    users_cart = json.loads(userdata.cart)
                    current_time = time.gmtime()
                    timestamp = calendar.timegm(current_time)
                    createOrder = order(id=id, userid=userid, user_firstname=firstname, user_lastname=lastname, user_email=email, user_company=company, user_address=address, user_city=city, user_zipcode=zipcode, order_cost=request.session['cost'], order_cart=users_cart, timestamp=timestamp)
                    createOrder.save()
                    request.session['user_order'] = id
                    data = json.loads(users.objects.get(id=request.session['user_login']).cart)
                    book_ids = list(data.values())
                    listings = Listings.objects.filter(id__in=book_ids)
                    for item in listings:
                        purchased_order = purchased_books(orderid=id, userid=request.session['user_login'], book_title=item.book_title, isbn=item.isbn, genre=item.genre, age_group=item.age_group, saleOrBorrow=item.saleOrBorrow, price=item.price, imgurl=item.imgurl, description=item.description, condition=item.condition, timestamp=timestamp)
                        purchased_order.save()
                    data = users.objects.get(id=request.session['user_login'])
                    data.cart = {}
                    data.save()
                    print('redirecting')
                    return redirect('payment', userid=userid)
                else:
                    userdata = users.objects.get(id=userid)
                    users_cart = json.loads(userdata.cart)
                    book_ids = list(users_cart.values())
                    listings = Listings.objects.filter(id__in=book_ids)
                    total_price = 0
                    for book in listings:
                        total_price = total_price + book.price
                    if total_price >= 50:
                        shipping = 0
                    else:
                        shipping = 5
                    tax = 0.08*total_price
                    total = total_price + shipping + tax
                    context = {
                        "userdata": userdata,
                        "listings": listings,
                        "total_price": total_price,
                        "tax": tax,
                        "shipping": shipping,
                        "total": total,
                        "userid": request.session['user_login'],
                    }
                    request.session['cost'] = total
                    template = loader.get_template("checkout.html")
                    return HttpResponse(template.render(context, request))
            else:
                return redirect('cart')
    else:
        return redirect('login')


def payment(request, userid):
    if 'user_login' in request.session:
        if str(request.session['user_login']) == userid:
            if request.POST.get('Pay'):
                del request.session['cost']
            else:
                total_price = request.session['cost']
                context = {
                    "total_price": total_price,
                }
                template = loader.get_template("payment.html")
                return HttpResponse(template.render(context, request))
        else:
            return redirect('cart')
    else:
        return redirect('login')


def chat(request, userid):
    return HttpResponse()