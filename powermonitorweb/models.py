from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    '''
    Alert model. Stores descriptions for each alert.
    '''
    alert_description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.alert_description

class UserAlerts(models.Model):
    '''
    Association class for Alert and UserProfile
    '''
    user_id = models.ForeignKey(User)
    alert_id = models.ForeignKey(Alert)
    alert_time = models.DateTimeField()

class AlertTip(models.Model):
    '''
    Tips for alerts
    '''
    tip_description = models.CharField(max_length=255)

class AlertTips(models.Model):
    '''
    Association class for Alert and AlertTip
    '''
    alert_id = models.ForeignKey(Alert)
    tip_id = models.ForeignKey(AlertTip)

class SocialMediaAccount(models.Model):
    '''
    Social media account info for each user
    '''
    account_type = models.CharField(max_length=255)
    account_username = models.CharField(max_length=255)
    # Still need to find a way to salt and hash the passwords. Assuming we need to store them
    account_password = models.CharField(max_length=255)

class UserSocialMedia(models.Model):
    '''
    Association class for UserProfile and UserSocialMedia
    '''
    user_id = models.ForeignKey(User)
    social_media_account_id = models.ForeignKey(SocialMediaAccount)

class Food(models.Model):
    '''
    Food items. A list of all possible food products will be kept
    '''
    food_description = models.CharField(max_length=255)
    food_spoiltime = models.TimeField()

    def __unicode__(self):
        return self.food_description

class HouseFoods(models.Model):
    '''
    Food products for the household
    '''
    food_id = models.ForeignKey(Food)

class ElectricityType(models.Model):
    '''
    Setup what type of electricity plan the household has
    '''
    plan_type = models.CharField(max_length=128)

    def __unicode__(self):
        return self.plan_type

class PrepaidTopups(models.Model):
    '''
    Prepaid topups for the household
    '''
    topup_date = models.DateTimeField(primary_key=True)
    topup_amount = models.FloatField()
    topup_units = models.IntegerField()

class PostPaid(models.Model):
    unit_cost = models.FloatField()

class IsSetup(models.Model):
    '''
    A simple boolean that stores whether the household has been setup or not.
    '''
    is_setup = models.BooleanField(null=False)