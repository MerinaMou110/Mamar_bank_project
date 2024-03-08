# Generated by Django 5.0.2 on 2024-03-08 03:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="bank_rupt",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="transaction",
            name="recipient_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="received_transactions",
                to="accounts.userbankaccount",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="transaction_type",
            field=models.IntegerField(
                choices=[
                    (1, "Deposite"),
                    (2, "Withdrawal"),
                    (3, "Loan"),
                    (4, "Loan Paid"),
                    (5, "Transfer Money"),
                ],
                null=True,
            ),
        ),
    ]