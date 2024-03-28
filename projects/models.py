from django.db import models
from django.conf import settings

def user_directory_path(instance, filename):
    return 'images/avatar/{0}/{1}'.format(instance.user.username, filename)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    website = models.URLField(blank=True)
    bio = models.CharField(max_length=240, blank=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    def __str__(self):
        return self.user.get_username()

    def get_absolute_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return '/path/to/default/avatar'
    
class News(models.Model):
    title = models.CharField(max_length=255, unique=True)
    body = models.TextField()
    image = models.ImageField(null = True, blank = True, upload_to="images/profile/" )
    date_created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True)
    subtitle = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

class Post(models.Model):
     
    class Meta: 
        ordering = ["-publish_date"]

    title = models.CharField(max_length=255, unique=True)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    body = models.TextField()
    meta_description = models.CharField(max_length=150, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=False)
    image = models.ImageField(null = True, blank = True, upload_to="images/profile/" )

    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True)

    def get_posts_by_tag(tag_name):
        return Post.objects.filter(tags__name__iexact=tag_name)