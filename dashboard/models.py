from django.db import models
from django.contrib.auth.models import AbstractUser, make_password
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import random
import string


class CustomUser(AbstractUser):
    is_verified =  models.BooleanField(default=False)
    legal_name = models.CharField(max_length=130, null=True, blank=True)


class Calls(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=70)
    size = models.CharField(max_length=60)
    crops = models.CharField(max_length=50)
    price_of_acre = models.IntegerField(null=True,blank=True)
    start_date = models.DateField(blank=True, null=True)
    projected_end_date = models.DateField(blank=True, null=True)
    rate = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

class Investments(models.Model):
    investor = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    call = models.ForeignKey(Calls, null=True, blank=True, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=130, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    size = models.IntegerField()
    price = models.IntegerField(null=True,blank=True)
    rate = models.IntegerField(null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.call: 
            self.rate = self.call.rate
            self.price = self.size * self.call.price_of_acre
        super(Investments, self).save(*args, **kwargs)


class Update(models.Model):
    call = models.ForeignKey(Calls, null=True, blank=True, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    body = models.TextField()


@receiver(post_save, sender=Calls)
def update_investments(sender, instance, **kwargs):
    investment_obj = Investments.objects.filter(call=instance)
    for obj in investment_obj:
        obj.rate =  instance.rate
        obj.price = obj.size * instance.price_of_acre
        obj.save()

def generate_random_word(length=12):
    # Define the characters we want to include in the word
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Randomly select characters and join them into a string
    random_word = ''.join(random.choice(characters) for _ in range(length))
    
    return random_word

@receiver(post_save, sender=Investments)
def send_verification_email(sender, instance, created, **kwargs):
    # Only execute the function when the investment is verified and hasn't been processed before
    if not created and instance.is_verified and instance.email and not hasattr(instance, '_sent_verification_email'):
        # Mark that the email has been sent for this instance to avoid recursion
        instance._sent_verification_email = True

        username = instance.email.split('@')[0]  
        password = generate_random_word()

        # Create or get the user
        user, user_created = CustomUser.objects.get_or_create(
            email=instance.email,
            defaults={
                'username': username,
                'password': make_password(password),  # Hash the password
                'legal_name': instance.full_name,  # Assuming 'investor' stores full name
            }
        )

        instance.investor = user
        instance.save()

        if user_created:
            # Send the verification email
            subject = "Your Investment Account is Verified!"
            message = f"Hello {instance.full_name},\n\nYour investment has been approved, and an account has been created for you.\n\nLogin details:\nUsername: {username}\nPassword: {password}\n\nPlease log in and change your password immediately for security.\n\nThank you!"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )
