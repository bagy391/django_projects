from django.shortcuts import render
from django.views import View
from django.conf import settings

from .models import ContactMessage
from django.contrib import messages

# Create your views here.
class HomeView(View):
    def get(self, request):
        # context = {
        #     'installed': settings.INSTALLED_APPS,
        #     'islocal': islocal
        # }
        print(settings.BASE_DIR)
        return render(request, 'myportfolio/index.html')

# myapp/views.py
from django.shortcuts import render, redirect
# from .forms import ContactMessageForm

def contact_view(request):
    if request.method == 'POST':
        try:
            ContactMessage.objects.create(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                subject=request.POST.get('subject'),
                message=request.POST.get('message')
            )
        except Exception:
            pass
        messages.success(request, 'Your message has been sent successfully!')
    return render(request, 'myportfolio/index.html')