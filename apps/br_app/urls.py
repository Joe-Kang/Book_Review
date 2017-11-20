from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^bookHome$', views.bookHome),
    url(r'^logout$', views.logout),
    url(r'^addPage$', views.addPage),
    url(r'^addBook$', views.addBook),
    url(r'^user/(?P<user_id>\d+)$', views.showUser),
    url(r'^book/(?P<book_id>\d+)$', views.showBook),
    url(r'^delete/(?P<book_id>\d+)$', views.delete)
]
