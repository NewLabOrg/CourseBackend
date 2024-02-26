from django.conf import settings
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphene import String
import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from graphene import Mutation, String, Field
from graphql import GraphQLError
from django.contrib.auth.hashers import make_password


from projects import models


class UserType(DjangoObjectType):
    website = graphene.String()
    bio = graphene.String()
    class Meta:
        model = get_user_model()
        fields = "__all__"

    def resolve_website(self, info):
        if hasattr(self, 'profile'):
            return self.profile.website
        return None

    def resolve_bio(self, info):
        if hasattr(self, 'profile'):
            return self.profile.bio
        return None       

class AuthorType(DjangoObjectType):
    profile_pic_url = String()

    class Meta: 
        model = models.Profile
        

    def resolve_profile_pic_url(self, info):
        if self.profile_pic:
            return info.context.build_absolute_uri(self.profile_pic.url)
        return ''

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
    new_by_slug = graphene.Field(NewsType, slug=graphene.String(required=True))
    viewer = graphene.Field(UserType, token=graphene.String(required=True))

    @login_required
    def resolve_viewer(self, info, **kwargs):
        return info.context.user

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
    
    def resolve_new_by_slug(root, _, slug):
        return models.News.objects.get(slug=slug)

    def resolve_posts_by_author(root, _, username):
        return models.Post.objects.prefetch_related("tags").select_related("author").filter(author__user__username=username)
    
    def resolve_posts_by_tag(root, _, tag):
        return models.Post.objects.prefetch_related("tags").select_related("author").filter(tags__name__iexact=tag)
    

class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, email, password, **kwargs):
        user = authenticate(info.context, email=email, password=password)

        if user is None:
            raise GraphQLError('Invalid credentials')

        info.context.user = user
        return cls(user=user)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

class CreateUser(Mutation):
    user = Field(UserType)

    class Arguments:
        username = String(required=True)
        password = String(required=True)
        email = String(required=True)
        firstname = String(required=True)
        lastname = String(required=True)
        website = String()
        bio = String()

    @transaction.atomic
    def mutate(self, info, username, password, email, firstname, lastname, website=None, bio=None):
        user = User(
            username=username,
            password=make_password(password),
            email=email,
            first_name=firstname,
            last_name=lastname,
        )
        user.save()

        author = models.Author(user=user)
        author.save()

        profile = models.Profile(user=user, website=website, bio=bio)
        profile.save()

        return CreateUser(user=user)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)