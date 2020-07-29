from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models


class ApprovalChoices(models.TextChoices):
    NEW = 'n', _('New')
    QUESTIONABLE = 'q', _('Questionable')
    ACCURATE = 'a', _('Accurate')
    VERIFIED = 'v', _('Verified')


class ApprovalChange(models.Model):
    change_from = models.CharField(max_length=1, choices=ApprovalChoices.choices)
    change_to = models.CharField(max_length=1, choices=ApprovalChoices.choices)
    change_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    reasoning = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    changed_object = GenericForeignKey('content_type', 'object_id')


class ApprovableModel(models.Model):
    approval_status = models.CharField(max_length=1, choices=APPROVAL_STATUSES, default=NEW)


class Author(ApprovableModel):
    name = models.CharField(max_length=1000)
    slug = models.SlugField()
    bio = models.TextField()
    webpage = models.URLField()


class Genre(ApprovableModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    description = models.TextField()
    exemplars = models.ManyToManyField('Book')
    parent = models.ForeignKey('self', on_delete=models.CASCADE)


class Book(ApprovableModel):
    isbn = models.CharField(max_length=13, unique=True, blank=True)
    title = models.CharField(max_length=5000)
    slug = models.SlugField()
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    blurb = models.TextField()
    reviews = models.TextField()


class LinkSource(ApprovableModel):
    TYPE_CHOICES = (
        ('i', 'Indie store'),
        ('d', 'Direct-from-creator store'),
        ('s', 'Store'),
        ('r', 'Review'),
        ('h', 'Homepage'),
        ('p', 'Publisher'),
        ('o', 'Other'),
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    homepage = models.URLField(blank=True)
    link_type = models.CharField(max_length=1, choices=TYPE_CHOICES)


class Link(ApprovableModel):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    source = models.ForeignKey('LinkSource', on_delete=models.CASCADE)
    url = models.URLField()
    clicks = models.IntegerField(default=0)
