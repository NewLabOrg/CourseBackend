from django.urls import path
from django.contrib import admin
from graphene_django.views import GraphQLView
from projects.schema import schema
from django.conf.urls.static import static
from graphql_jwt.decorators import jwt_cookie
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from graphene_file_upload.django import FileUploadGraphQLView



class CustomGraphQLView(FileUploadGraphQLView):
    pass

custom_graphql_view = jwt_cookie(csrf_exempt(CustomGraphQLView.as_view(graphiql=True, schema=schema)))

class CustomGraphQLView(FileUploadGraphQLView):
    @jwt_cookie
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', CustomGraphQLView.as_view(graphiql=True, schema=schema)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)