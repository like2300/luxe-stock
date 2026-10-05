import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockpro.settings")
django.setup()

import re

from django.contrib.auth.models import User
from django.test import Client

from core.models import Membership

m = Membership.objects.select_related("shop").filter(is_owner=True).first()
if not m:
    m = Membership.objects.select_related("shop").first()
print("member:", m and m.user.username)

c = Client()
c.force_login(m.user)

r = c.get("/produits/", SERVER_NAME="127.0.0.1")
print("page:", r.status_code)
html = r.content.decode()

r2 = c.get("/api/suggestions/produits/", {"q": "a"}, SERVER_NAME="127.0.0.1")
print("suggest:", r2.status_code, r2.content[:300])

inputs = re.findall(r"<input[^>]*name=\"q\"[^>]*>", html)
for i in inputs:
    print("input:", i)
print("suggest.js loaded:", "js/suggest.js" in html)

# Liste des produits de la boutique pour savoir ce que renverrait la recherche
prods = list(m.shop.products.values_list("name", flat=True)[:10])
print("products:", prods)
