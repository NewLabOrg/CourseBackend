from cProfile import Profile
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
from graphene_file_upload.scalars import Upload
from django.core.files.base import ContentFile
import uuid
from .models import Post, Tag, Profile
from django.utils.text import slugify
from django.utils import timezone


from projects import models

current_time = timezone.now()
class UserType(DjangoObjectType):
    website = graphene.String()
    bio = graphene.String()
    profile_image_url = graphene.String()

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
    

    def resolve_profile_image_url(self, info):
        
        if hasattr(self, 'profile') and self.profile.image:
            return info.context.build_absolute_uri(self.profile.image.url)
        return None

class UploadProfilePic(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)
        userId = graphene.ID(required=True)

    success = graphene.Boolean()
    url = graphene.String()

    @staticmethod
    def mutate(root, info, file, userId):
        if not file:
            raise Exception('Файл не был предоставлен')
        
        if not hasattr(file, 'name'):
            raise Exception("Полученный объект не содержит атрибута 'name'")

        try:
            user = User.objects.get(pk=userId)
            profile, created = Profile.objects.get_or_create(user=user)
            filename = f"{uuid.uuid4()}-{file.name}"
            profile.image.save(filename, ContentFile(file.read()), save=True)
            url = info.context.build_absolute_uri(profile.image.url)
            return UploadProfilePic(success=True, url=url)
        except User.DoesNotExist:
            raise Exception('Пользователь не найден')


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
        fields = ( "title", "slug", "subtitle", "image", "image_url")
    
    def resolve_image_url(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return ''
    
class PostType(DjangoObjectType):
    image_url = graphene.String()

    class Meta:
        model = models.Post
        fields = ('id', "title", "slug", "subtitle", "body", "meta_description", "date_created", "date_modified", "publish_date", "published", "image", "image_url", "author", "tags")

    def resolve_image_url(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return ''




class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        subtitle = graphene.String()
        body = graphene.String(required=True)
        author_username = graphene.String(required=True)
        tags = graphene.List(graphene.String)
        image = Upload()  

    post = graphene.Field(PostType)

    @staticmethod
    def mutate(root, info, title, subtitle, body, author_username, tags=None, image=None):
       
        slug = slugify(title)
        
        num = 1
        original_slug = slug
        while Post.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{num}"
            num += 1

        
        meta_description = body[:150] if len(body) > 150 else body

      
        try:
            author_profile = Profile.objects.get(user__username=author_username)
        except Profile.DoesNotExist:
            raise Exception('Автор не найден')

       
        post = Post(
            title=title,
            subtitle=subtitle,
            slug=slug,
            body=body,
            meta_description=meta_description,
            publish_date=timezone.now(),  
            published=True,  
            author=author_profile,
            image=image if image else None
        )
        post.save()

        
        if tags:
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)

        return CreatePost(post=post)

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
    user = graphene.Field(UserType, username=graphene.String(required=True))

    def resolve_user(self, info, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
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
    


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        firstname = graphene.String(required=True)
        lastname = graphene.String(required=True)
        website = graphene.String()
        bio = graphene.String()
        image = Upload()

    @transaction.atomic
    def mutate(self, info, username, password, email, firstname, lastname, website=None, bio=None, image=None):
        user = User(
            username=username,
            email=email,
            first_name=firstname,
            last_name=lastname,
        )
        user.set_password(password)
        user.save()

        profile = Profile(user=user, website=website, bio=bio)

        if image:
            filename = f'{uuid.uuid4()}{os.path.splitext(image.name)[-1]}'
            profile.image.save(filename, ContentFile(image.read()), save=True)

        profile.save()

        return CreateUser(user=user)
    
    
class UploadFile(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    success = graphene.Boolean()

    def mutate(self, info, file, **kwargs):
        return UploadFile(success=True)

class Mutation(graphene.ObjectType):
    upload_file = UploadFile.Field()

schema = graphene.Schema(mutation=Mutation)
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    upload_profile_pic = UploadProfilePic.Field()
    create_post = CreatePost.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)