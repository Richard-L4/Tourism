from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.CharField()

    def __str__(self):
        return f"{self.name} | {self.email}"

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"


class CardText(models.Model):
    title = models.CharField(max_length=50, blank=True)
    content = models.TextField()
    image_name = models.CharField(
        max_length=30,
        help_text="Enter the image filename (eg 'science museum.jpg)",
        default='default.jpg',
        blank=True
    )

    saved_by = models.ManyToManyField(User,
                                      related_name='saved_cards', blank=True)

    def __str__(self):
        return self.title or f"Card for {self.image_name}"


class Comment(models.Model):
    card = models.ForeignKey(
        CardText,
        on_delete=models.CASCADE,
        related_name='comments',
        default=1
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.text[:30]}"
