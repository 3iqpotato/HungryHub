from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='users/', null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    address = models.TextField(blank=True, default="")


    #TODO test dali naistina raboti i iztriva da ne stava mazalo!!!
    def save(self, *args, **kwargs):
        # Ако вече съществува запис в базата (update, а не create)
        if self.pk:
            try:
                old_instance = UserProfile.objects.get(pk=self.pk)
                # Проверка дали img е променен и старият не е празен
                if old_instance.img and old_instance.img != self.img:
                    # Това работи и с AzureStorage, и с FileSystemStorage
                    old_instance.img.delete(save=False)
            except UserProfile.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Изтриваме файла и при изтриване на целия профил
        if self.img:
            self.img.delete(save=False)
        super().delete(*args, **kwargs)

    def is_complete(self):
        """
        Профилът е завършен само ако address и phone
        не са празни и не съдържат само интервали.
        """
        address_ok = bool(self.address and self.address.strip())
        phone_ok = bool(self.phone_number and self.phone_number.strip())
        return address_ok and phone_ok