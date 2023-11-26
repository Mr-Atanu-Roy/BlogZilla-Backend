from django.db import models
from django.contrib.auth.models import AbstractUser

from .manager import Usermanager
from .utils import BaseModel

import uuid

from autoslug import AutoSlugField

#custom user model
class User(AbstractUser):
    username = None

    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    last_logout = models.DateTimeField(null=True, blank=True)
    
    phone = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=300, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', blank=True)
    country = models.CharField(max_length=80, blank=True)

    objects = Usermanager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'auth_user'
        verbose_name_plural = "BlogZilla User"

    #func to get full name of user
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.email
    


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    profile_is_complete = models.BooleanField(default=False)

    bio = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True)
    interests = models.CharField(max_length=500, blank=True)
    
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)

    # last_paid = models.DateTimeField(null=True, blank=True)
    # plan_expiry = models.DateTimeField(null=True, blank=True)
    # plan = models.ForeignKey(Plan, default=1, on_delete=models.SET_DEFAULT, related_name='user_plan')
    
    class Meta:
        verbose_name_plural = "BlogZilla User Profile"
    
    def __str__(self):
        return str(self.user)
    



class Tokens(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.UUIDField(default = uuid.uuid4, editable = False, unique=True)
    use = models.CharField(max_length=100, default='reset-password', choices=(
        ('reset-password', 'reset-password'),
    ))    
    is_expired = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Tokens"
    
    def __str__(self):
        return str(self.user)



'''
class Plans(BaseModel):
    name = models.CharField(max_length=100, blank=False)
    price = models.IntegerField(default=0)
    validity_days = models.IntegerField(default=30)

    read_blogs = models.BooleanField(default=True)
    publish_blogs = models.BooleanField(default=False)
    no_publish_blogs = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "BlogZilla Plans"
    
    def __str__(self):
        return self.name
'''

class Blog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    
    published = models.BooleanField(default=False)
    title = models.CharField(max_length=500, blank=False)
    slug = AutoSlugField(populate_from='title', unique=True)

    header_img = models.ImageField(upload_to='blog_header_img/', blank=False) 
    content = models.TextField()

    tags = models.CharField(max_length=800, blank=True)

    likes_no = models.IntegerField(default=0)
    comments_no = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Blogs"
    
    def __str__(self):
        return self.title


    

class BlogComments(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_comments')
    comment = models.TextField()

    likes_no = models.IntegerField(default=0)
    comments_no = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Blog Comments"
    
    def __str__(self):
        return f"{self.user}"




class BlogLikes(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_likes')
    
    class Meta:
        verbose_name_plural = "Blog Likes"
    
    def __str__(self):
        return f"{self.user} - {self.blog}"


class ReplyComments(BaseModel):
    '''
    holds reply comments for both blog comments and reply comments. Each ReplyComments object will have either parent_blog_comment or parent_reply_comment to null
    '''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    parent_blog_comment = models.ForeignKey(BlogComments, on_delete=models.CASCADE, related_name='reply_comments', null=True, blank=True)
    parent_reply_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    comment = models.TextField()

    likes_no = models.IntegerField(default=0)
    comments_no = models.IntegerField(default=0)


    #overriding save method to make sure parent_blog_comment or parent_reply_comment both are not null
    def save(self, *args, **kwargs):
        if self.parent_blog_comment is None and self.parent_reply_comment is None:
            raise ValueError('Both parent_blog_comment and parent_reply_comment cannot be null')
        elif self.parent_blog_comment is not None and self.parent_reply_comment is not None:
            raise ValueError('Both parent_blog_comment and parent_reply_comment can not be added')
    
        super(ReplyComments, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Comments Reply"
    
    def __str__(self):
        return f"{self.user}"



class LikeComments(BaseModel):
    '''
    holds likes for both blog comments and reply comments. Each LikeComments object will have either parent_blog_comment or parent_reply_comment to null
    '''

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    parent_blog_comment = models.ForeignKey(BlogComments, on_delete=models.CASCADE, related_name='like_blog_comments', blank=True, null=True)
    parent_reply_comment = models.ForeignKey(ReplyComments, on_delete=models.CASCADE, related_name='like_reply_comments', blank=True, null=True)

    #overriding save method to make sure parent_blog_comment or parent_reply_comment both are not null
    def save(self, *args, **kwargs):
        if self.parent_blog_comment is None and self.parent_reply_comment is None:
            raise ValueError('Both parent_blog_comment and parent_reply_comment cannot be null')
        super(LikeComments, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Comments Like"
    
    def __str__(self):
        return f"{self.user}"


