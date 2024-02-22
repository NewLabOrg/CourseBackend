from django.conf import settings
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphene import String
import graphene


from projects import models

User = get_user_model()
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"

class AuthorType(DjangoObjectType):
    class Meta: 
        model = models.Profile

class NewsType(DjangoObjectType):
    image_url = String()

    class Meta:
        model = models.News
        fields = ("title", "slug", "subtitle", "image", "image_url")
    
    def resolve_image_url(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return ''
    
class PostType(DjangoObjectType):
    image_url = String()

    class Meta:
        model = models.Post
        fields = ("title", "slug", "subtitle", "body", "meta_description", "date_created", "date_modified", "publish_date", "published", "image", "image_url", "author", "tags")

    def resolve_image_url(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return ''
    class Meta:
        model = models.Post
        fields = ("title", "slug", "subtitle", "body", "meta_description", "date_created", "date_modified", "publish_date", "published", "image", "image_url", "author", "tags")

    def resolve_image_url(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return ''

class TagType(DjangoObjectType):
    class Meta: 
        model = models.Tag

class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    author_by_username = graphene.Field(AuthorType, username=graphene.String(required=True))
    post_by_slug = graphene.Field(PostType, slug=graphene.String(required=True))
    post_by_author = graphene.List(PostType, username=graphene.String(required=True))
    posts_by_tag = graphene.List(PostType, tag=graphene.String(required=True))
    get_news = graphene.List(NewsType)

    def resolve_all_posts(root, _):
        return models.Post.objects.prefetch_related("tags").select_related("author").all()
    
    def resolve_author_by_username(root, _, username):
        return models.Profile.objects.select_related("user").get(user__username=username)
    
    def resolve_get_news(root, _):
        return models.News.objects.all()
    
    def resolve_get_news_by_slug(root, _, slug):
        return models.News.objects.get(slug=slug)
    
    def resolve_post_by_slug(root, _, slug):
        return models.Post.objects.get(slug=slug)

    def resolve_posts_by_author(root, _, username):
        return models.Post.objects.prefetch_related("tags").select_related("author").filter(author__user__username=username)
    
    def resolve_posts_by_tag(root, _, tag):
        return models.Post.objects.prefetch_related("tags").select_related("author").filter(tags__name__iexact=tag)

schema = graphene.Schema(query=Query)
