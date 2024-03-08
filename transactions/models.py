from django.db import models
from accounts.models import UserBankAccount
# Create your models here.
from . constants import TRANSACTION_TYPE
class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name = 'transactions', on_delete = models.CASCADE) # ekjon user er multiple transactions hote pare
    recipient_account = models.ForeignKey(UserBankAccount, related_name='received_transactions', null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(decimal_places=2, max_digits = 12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits = 12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False) 
    bank_rupt = models.BooleanField(default=False)
    class Meta:
        ordering = ['timestamp']  #sort korbe timestamp onujayi
 