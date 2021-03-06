from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from .facebook_methods import get_graph

# Create your models here.


class FacebookUser(models.Model):
    """Facebook User

    Has some info about the Facebook OAuth user.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    access_token = models.TextField()

    # Scope User ID
    social_id = models.TextField(unique=True)

    # Last time the user was updated
    updated_at = models.DateTimeField(auto_now=True)

    # Expiration time
    expires = models.IntegerField()

    first_name = models.CharField(max_length=50)
    name = models.CharField(max_length=150)

    thumbnail = models.CharField(max_length=2000, null=True)
    thumbnail_age = models.DateTimeField(null=True)

    # Direct link to user's profile
    link = models.URLField(max_length=2000)

    @property
    def is_expired(self):

        # Returns true if expired. False otherwise
        return timezone.now() > self.updated_at + datetime.timedelta(seconds=self.expires)

    @property
    def picture(self):

        # Fetches a 500x500 picture from the user. On demand
        return get_graph().get_object(str(self.social_id) + "/picture?width=500&height=500")['url']

    @staticmethod
    def create_or_update(social_id, access_token, expires, first_name, name, link, user):
        """Create or Update a Facebook User

        Receives a social_id and, if not yet saved, creates a new FacebookUser
        Update it otherwise
        """

        # Tries to find the user
        if FacebookUser.objects.filter(social_id=social_id):

            # Case where the user is already registered and tries to register again
            if user is not None:
                return None

            # if it is found, get it and update it
            obj = FacebookUser.objects.get(social_id=social_id)
            obj.access_token = access_token
            obj.expires = expires
            obj.first_name = first_name
            obj.name = name
            obj.link = link
            print('USER UPDATED')

        else:
            def f_usname(name, n=0):
                """
                appends n to the end of the username, automatically adding 1 if exists
                """
                if not User.objects.filter(username=name + '_' + str(n)).exists():
                    return name + '_' + str(n)
                return f_usname(name, n + 1)

            # If it is not found, and user is None, don't create a new facebookuser
            if user is None:
                print('USER NOT REGISTERED')
                return None
            # else, create a new facebookuser
            obj = FacebookUser(
                user=user,
                social_id=social_id,
                access_token=access_token,
                expires=expires,
                first_name=first_name,
                name=name,
                link=link
            )
            user.username = f_usname(name)
            user.is_active = True
            user.save()
            print('USER CREATED')
        obj.save()

        # Hotfix: link user.teacher.facebookuser or student to this
        user = obj.user.teacher_or_student
        if user is not None:
            user.facebookuser = obj
            user.has_facebook = True
            user.save()

        return obj

    def __str__(self):
        return self.name
