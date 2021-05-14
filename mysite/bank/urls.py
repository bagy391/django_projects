from django.urls import path
from . import views

# https://docs.djangoproject.com/en/3.0/topics/http/urls/
app_name='bank'
urlpatterns = [
  path('', views.MainView.as_view(), name='all'),
  path('lookup/cust', views.CustView.as_view(), name='customers_list'),
  path('bank/<int:pk>', views.CustomersDetailView.as_view(), name='customers_detail'),
  path('main/create/', views.CustCreate.as_view(), name='customers_create'),
  path('main/<int:pk>/update/', views.CustUpdate.as_view(), name='customers_update'),
  path('main/<int:pk>/delete/', views.CustDelete.as_view(), name='customers_delete'),
  path('lookup/trans', views.TransView.as_view(), name='trans_list'),
  path('main/<int:pk>/',views.TransferToView.as_view(), name='transfer_to'),
]