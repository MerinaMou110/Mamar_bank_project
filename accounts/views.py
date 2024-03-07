from django.shortcuts import  HttpResponseRedirect,render
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm
#django amaderk login korar subidha dey
from django.contrib.auth import login,logout

from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import redirect

# Create your views here.
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
    
    