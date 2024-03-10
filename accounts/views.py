from django.shortcuts import  HttpResponseRedirect,render
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm,CustomPasswordChangeForm
#django amaderk login korar subidha dey
from django.contrib.auth import login,logout

from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import redirect
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
# Create your views here.

def send_email_user(user,  subject, template):
        message = render_to_string(template, {
            'user' : user,
            
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register')  #form submit korar por profile page a ashbe
    
    def form_valid(self,form):
        print(form.cleaned_data)
        # Save the form data to create a new user and related models
        user = form.save()    #form.save korle 3 ta model er data akshate save hoa jabe
        login(self.request, user) #user er data gulo dia login korbo
        print(user)
        return super().form_valid(form) # form_valid function call hobe jodi sob thik thake
    

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        messages.success(
            self.request,
            f'Your Account Logged in successfully'
        )
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')
    


class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    
    




class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')  # Update with the URL name of your profile page

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        # Send email notification about the password change
        
        send_email_user(self.request.user,  "Password Change Notification", "accounts/update_email.html")

        messages.success(self.request, 'Your password has been changed successfully.')
        return response
