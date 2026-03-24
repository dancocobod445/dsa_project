from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.book_list,       name='book_list'),
    path('my-books/',                   views.my_books,        name='my_books'),
    path('add/',                        views.add_book,        name='add_book'),
    path('remove/<int:book_id>/',       views.remove_book,     name='remove_book'),
    path('borrow/<int:book_id>/',       views.borrow_book,     name='borrow_book'),
    path('request/<int:req_id>/approve/', views.approve_request, name='approve_request'),
    path('request/<int:req_id>/reject/',  views.reject_request,  name='reject_request'),
    path('request/<int:req_id>/return/',  views.return_book,     name='return_book'),
    path('search/',                     views.search_books,    name='search_books'),
    path('history/',                    views.history,         name='history'),
    path('book/<int:book_id>/',         views.book_detail,     name='book_detail'),
    path('dashboard/',                  views.admin_dashboard, name='admin_dashboard'),
    path('stats/<str:stat>/',           views.stat_detail,     name='stat_detail'),
]
