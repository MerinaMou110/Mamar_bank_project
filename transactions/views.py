from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from transactions.constants import DEPOSIT, WITHDRAWAL,LOAN, LOAN_PAID,TRANSFER
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from django.db.models import Sum
from accounts.models import UserBankAccount

# Create your views here.
from transactions.forms import (
    DepositForm,
    WithdrawForm,
    LoanRequestForm,
    TransferForm
)
from transactions.models import Transaction

def send_transection_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

def send_transfer_transection_email(user,receiver, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'receiver' : receiver,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()




# aI view k inherit kore amra deposite, withdraw, loan request er kaj korbo
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    #loading time komanor jonno reverse lazy use kora hoy
    success_url = reverse_lazy('transaction_report')
     
    # jokhn obj toiri hobe tokhn e jodi kono kaj korte chai tahole get_form_kwargs
    # views theke kaj kortesi
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # template e context data pass kora
        context.update({
            'title': self.title
        })

        return context
    


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        account.balance += amount # amount = 200, tar ager balance = 0 taka new balance = 0+200 = 200
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )

        send_transection_email(self.request.user, amount, "Deposite Message", "transactions/deposite_email.html")

        return super().form_valid(form)




class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        
        if Transaction.objects.filter(bank_rupt=True).exists():
            messages.error(
                self.request,
                'The bank is bankrupt. Withdrawals are not allowed at the moment.'
            )
            return redirect('withdraw_money')
        


        self.request.user.account.balance -= form.cleaned_data.get('amount')
        # balance = 300
        # amount = 5000
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )

        send_transection_email(self.request.user, amount, "withdrawal Message", "transactions/withdrawal_email.html")

        return super().form_valid(form)



class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")
        messages.success(
            self.request,
            f'Lo an request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )
        send_transection_email(self.request.user, amount, "Loan Request Message", "transactions/loan_email.html")

        return super().form_valid(form)
    




# shob gulo transaction k akbare dekhano k bole lostview
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0 # filter korar pore ba age amar total balance ke show korbe
    
    def get_queryset(self):
        # jodi user kono type filter nh kore taile tar total transition report dekhabo
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            

            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)

            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
       
        return queryset.distinct() # unique queryset hote hobe
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })

        return context
    
        
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        print(loan)
        if loan.loan_approve: #akjon user loan pay korte parbe tokhni jokhn tar loan approve hobe
            user_account = loan.account
                # Reduce the loan amount from the user's balance
                # 5000, 500 + 5000 = 5500
                # balance = 3000, loan = 5000
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(
            self.request,
            f'Loan amount is greater than available balance'
        )

        return redirect('loan_list')


class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' # loan list ta ei loans context er moddhe thakbe
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account,transaction_type=3)
        print(queryset)
        return queryset
    




class TransferMoneyView(TransactionCreateMixin):
    
    form_class = TransferForm
    title = 'Transfer Money'

    def get_initial(self):
        initial = {'transaction_type': TRANSFER}
        return initial
    print(f"Recipient Account (form_valid): ")
    def form_valid(self, form):
        
        recipient_account = form.cleaned_data.get('recipient_account_number')
        print(f"Recipient Account (form_valid): {recipient_account}")
        amount = form.cleaned_data.get('amount')

        # Check if the recipient account exists
        if not recipient_account:
            messages.error(self.request, 'Recipient account not found.')
            # return redirect('transfer_money')
        
        sender_account = self.request.user.account
        recipient_account = UserBankAccount.objects.get(account_no=recipient_account)  # Fetch the actual UserBankAccount instance
        
        recipient_account.balance += amount
        sender_account.balance -= amount
        

        recipient_account.save()
        sender_account.save()

        messages.success(
            self.request,
            f'Successfully transferred {"{:,.2f}".format(float(amount))}$ to {recipient_account.user.username}'
        )
        # Send email notification to both sender and recipient
        send_transfer_transection_email(self.request.user,recipient_account.user, amount, "Transfer Message", "transactions/transfer_email.html")
        send_transfer_transection_email(recipient_account.user,self.request.user, amount, "Transfer Message", "transactions/transfer_receiver_email.html")

        return super().form_valid(form)
   
