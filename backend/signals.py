from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from backend.models import User, UserProfile, Tokens, BlogComments, BlogLikes, ReplyComments, LikeComments
from .utils import EmailSender


#signals

@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, *args, **kwargs):
    '''
    creates a UserProfile when a new User is created and send email verification link to user
    '''

    try:
        #execute only if db record is created
        if created:    
            user_profile = UserProfile(user=instance)
            user_profile.save()

            #send email verification link to user
            EmailSender(instance.email).email_verify_link_send(
                user=instance, 
                name=instance.get_full_name(),
            )

    except Exception as e:
        print(e)
        pass


@receiver(post_save, sender=Tokens)
def token_created_handler(sender, instance, created, *args, **kwargs):
    '''
    send appropriate link when a token is generated
    '''

    try:
        #execute only if db record is created
        if created:    
            if instance.use == "reset-password":
               EmailSender(instance.user.email).reset_password_link_send(
                   user=instance.user, 
                   name=instance.user.get_full_name(), 
                   token=instance.token
                )

    except Exception as e:
        print(e)
        pass



@receiver(post_save, sender=BlogComments)
def blog_comment_create_handler(sender, instance, created, *args, **kwargs):
    '''
    increase the comments_no of the Blog by 1 when a new BlogComments is created
    '''

    try:
        #execute only if db record is created
        if created:    
            blog = instance.blog
            if blog.comments_no >= 0:
                blog.comments_no += 1
                blog.save()

    except Exception as e:
        print(e)
        pass



@receiver(pre_delete, sender=BlogComments)
def blog_comment_delete_handler(sender, instance, *args, **kwargs):
    '''
    decrease the comments_no of the Blog by 1 when a BlogComments is deleted
    '''

    try:
        blog = instance.blog
        if blog.comments_no >= 1:
            blog.comments_no -= 1
            blog.save()

    except Exception as e:
        print(e)
        pass



@receiver(post_save, sender=BlogLikes)
def blog_like_created_handler(sender, instance, created, *args, **kwargs):
    '''
    increase the likes_no of the Blog by 1 when a new BlogLikes is created
    '''

    try:
        #execute only if db record is created
        if created:    
            blog = instance.blog
            if blog.likes_no >= 0:
                blog.likes_no += 1
                blog.save()

    except Exception as e:
        print(e)
        pass




@receiver(pre_delete, sender=BlogLikes)
def blog_like_delete_handler(sender, instance, *args, **kwargs):
    '''
    decrease the likes_no of the Blog by 1 when a BlogLikes is deleted
    '''

    try:
        blog = instance.blog
        if blog.likes_no >= 1:
            blog.likes_no -= 1
            blog.save()

    except Exception as e:
        print(e)
        pass



@receiver(post_save, sender=ReplyComments)
def reply_comment_created_handler(sender, instance, created, *args, **kwargs):
    '''
    increase the likes_no of the BlogComment by 1 when a new ReplyComments is created
    '''

    try:
        #execute only if db record is created
        if created:    
            parent_blog_comment = instance.parent_blog_comment
            parent_reply_comment = instance.parent_reply_comment

            if parent_blog_comment is not None:
                if parent_blog_comment.comments_no >= 0:
                    parent_blog_comment.comments_no += 1
                    parent_blog_comment.save()

            elif parent_reply_comment is not None:
                if parent_reply_comment.comments_no >= 0:
                    parent_reply_comment.comments_no += 1
                    parent_reply_comment.save()


    except Exception as e:
        print(e)
        pass




@receiver(pre_delete, sender=ReplyComments)
def reply_comment_delete_handler(sender, instance, *args, **kwargs):
    '''
    increase the likes_no of the BlogComment by 1 when a ReplyComments is deleted
    '''

    try:  
        parent_blog_comment = instance.parent_blog_comment
        parent_reply_comment = instance.parent_reply_comment

        if parent_blog_comment is not None:
            if parent_blog_comment.comments_no >= 1:
                parent_blog_comment.comments_no -= 1
                parent_blog_comment.save()

        elif parent_reply_comment is not None:
            if parent_reply_comment.comments_no >= 1:
                parent_reply_comment.comments_no -= 1
                parent_reply_comment.save()


    except Exception as e:
        print(e)
        pass




@receiver(post_save, sender=LikeComments)
def like_comment_created_handler(sender, instance, created, *args, **kwargs):
    '''
    increase the likes_no of the BlogComment by 1 when a new LikeComment is created
    '''

    try:
        #execute only if db record is created
        if created:    
            parent_blog_comment = instance.parent_blog_comment
            parent_reply_comment = instance.parent_reply_comment

            if parent_blog_comment is not None:
                if parent_blog_comment.like_no >= 0:
                    parent_blog_comment.like_no += 1
                    parent_blog_comment.save()

            elif parent_reply_comment is not None:
                if parent_reply_comment.like_no >= 0:
                    parent_reply_comment.like_no += 1
                    parent_reply_comment.save()


    except Exception as e:
        print(e)
        pass



@receiver(pre_delete, sender=LikeComments)
def like_comment_delete_handler(sender, instance, *args, **kwargs):
    '''
    increase the likes_no of the BlogComment by 1 when a LikeComment is deleted
    '''

    try:
        parent_blog_comment = instance.parent_blog_comment
        parent_reply_comment = instance.parent_reply_comment

        if parent_blog_comment is not None:
            if parent_blog_comment.like_no >= 1:
                parent_blog_comment.like_no -= 1
                parent_blog_comment.save()

        elif parent_reply_comment is not None:
            if parent_reply_comment.like_no >= 1:
                parent_reply_comment.like_no -= 1
                parent_reply_comment.save()


    except Exception as e:
        print(e)
        pass



