from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='users/', null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    address = models.TextField(blank=True, default="")

    def is_complete(self):
        """
        Профилът е завършен само ако address и phone
        не са празни и не съдържат само интервали.
        """
        address_ok = bool(self.address and self.address.strip())
        phone_ok = bool(self.phone_number and self.phone_number.strip())
        return address_ok and phone_ok