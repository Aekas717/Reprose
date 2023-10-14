from django.db import models

# Create your models here.


class users(models.Model):
    id = models.IntegerField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email_id = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    cart = models.JSONField(default=dict)


class Listings(models.Model):
    id = models.IntegerField(primary_key=True)
    # This is related to the previous model
    userid = models.IntegerField()
    book_title = models.CharField(max_length=100)
    isbn = models.IntegerField()
    genre = models.CharField(max_length=100)
    age_group = models.CharField(max_length=20)
    saleOrBorrow = models.CharField(max_length=20)
    price = models.IntegerField()
    imgurl = models.CharField(max_length=255)
    description = models.CharField(max_length=700)
    condition = models.CharField(max_length=50)
    times_viewed = models.IntegerField()
    borrowed_date = models.BigIntegerField()

class order(models.Model):
    id = models.CharField(primary_key=True, max_length=16)
    userid = models.IntegerField()
    user_firstname = models.CharField(max_length=50)
    user_lastname = models.CharField(max_length=50)
    user_email = models.CharField(max_length=50)
    user_company = models.CharField(max_length=50)
    user_address = models.CharField(max_length=50)
    user_city = models.CharField(max_length=50)
    user_zipcode = models.IntegerField()
    order_cost = models.IntegerField()
    order_cart = models.JSONField(default = dict)
    timestamp = models.PositiveBigIntegerField()

class purchased_books(models.Model):
    id = models.IntegerField(primary_key=True)
    orderid = models.CharField(max_length=16)
    userid = models.IntegerField()
    book_title = models.CharField(max_length=100)
    isbn = models.IntegerField()
    genre = models.CharField(max_length=100)
    age_group = models.CharField(max_length=20)
    saleOrBorrow = models.CharField(max_length=20)
    price = models.IntegerField()
    imgurl = models.CharField(max_length=255)
    description = models.CharField(max_length=700)
    condition = models.CharField(max_length=50)
    timestamp = models.PositiveBigIntegerField()
