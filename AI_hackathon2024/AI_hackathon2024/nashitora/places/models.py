from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.
# 観光地を表す Place モデルを定義します。


class Place(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    opening_hours = models.CharField(max_length=100, blank=True)
    access = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Photo(models.Model):
    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name='photos')
    media_url = models.URLField()
    caption = models.TextField(blank=True, null=True)
    permalink = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Photo of {self.place.name}"


class Hashtag(models.Model):

    number = models.IntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)])
    category = models.CharField(max_length=100, validators=[
                                MinLengthValidator(1)])
    spot = models.CharField(max_length=100, validators=[MinLengthValidator(1)])
    address = models.CharField(max_length=100, validators=[
                               MinLengthValidator(1)])
    latitude = models.FloatField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)])
    longitude = models.FloatField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)])

    class Meta:
        verbose_name = '観光地'
        verbose_name_plural = '観光地リスト'

    def return_number(self):
        return (self.number)
