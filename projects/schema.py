from django.conf import settings
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
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
    
class PostType(DjangoObjectType):
    class Meta:
        model = models.Post

class TagType(DjangoObjectType):
    class Meta: 
        model = models.Tag

class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    author_by_username = graphene.Field(AuthorType, username=graphene.String(required=True))
    post_by_slug = graphene.Field(PostType, slug=graphene.String(required=True))
    post_by_author = graphene.List(PostType, username=graphene.String(required=True))
    posts_by_tag = graphene.List(PostType, tag=graphene.String(required=True))

    def resolve_all_posts(root, info):
        return models.Post.objects.prefetch_related("tags").select_related("author").all()
    
    def resolve_author_by_username(root, info, username):
        return models.Profile.objects.select_related("user").get(user__username=username)
    
    def resolve_post_by_slug(root, info, slug):
        return models.Post.objects.get(slug=slug)

    def resolve_posts_by_author(root, info, username):
        return models.Post.objects.prefetch_related("tags").select_related("author").filter(author__user__username=username)
    
    def resolve_posts_by_tag(root, info, tag):
        return models.Post.objects.prefetch_related("tags").select_related("author").filter(tags__name__iexact=tag)

schema = graphene.Schema(query=Query)
