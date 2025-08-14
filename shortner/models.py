from django.db import models
from django.utils import timezone
import secrets
import string

class ShortURL(models.Model):
    original_url = models.URLField(max_length=1000)
    short_code = models.CharField(max_length=8, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_code(cls, length=6):
        alphabet = string.ascii_letters + string.digits
        for _ in range(10):  # try 10 times to avoid collision
            code = "".join(secrets.choice(alphabet) for _ in range(length))
            if not cls.objects.filter(short_code=code).exists():
                return code
        return cls.generate_unique_code(length + 1)

    def touch(self):
        self.clicks = models.F("clicks") + 1
        self.last_accessed = timezone.now()
        self.save(update_fields=["clicks", "last_accessed"])

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
