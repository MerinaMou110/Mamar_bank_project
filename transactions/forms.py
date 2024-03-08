from django import forms 
from .models import Transaction
from accounts.models import UserBankAccount
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type',
            'recipient_account',
        ]

# transaction er kj hobe backend theke. user transaction choice jate nh korte pare
        # user er account pass korsi aikhane
    def __init__(self, *args, **kwargs):
        # self.account a  user account save korsi
        self.account = kwargs.pop('account') # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    #save korar jonno
    def save(self, commit=True):
        # j user rwquest kortese tar object jodi database a thake shei instance er account a jabo
        self.instance.account = self.account
        # new balance dia update korsi.  500 tk ase. deposit korbo 300. total=800
        self.instance.balance_after_transaction = self.account.balance  # 0--->5000
        return super().save()



 # Transaction form theke inherite korbe deposit, withdraw,loan form   
class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount
    

class WithdrawForm(TransactionForm):

    def clean_amount(self):
        #
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance # 1000
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )
        if amount > balance: # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount
    



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount
    


class TransferForm(TransactionForm):
    recipient_account_number = forms.CharField(label='Recipient Account Number', max_length=20)

  
    def clean_recipient_account_number(self):
        recipient_account_number = self.cleaned_data.get('recipient_account_number')
        try:
            recipient_account =UserBankAccount.objects.get(account_no=recipient_account_number)
            return recipient_account.account_no
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError('Recipient account not found.')
            