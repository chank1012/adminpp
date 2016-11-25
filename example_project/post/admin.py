from django.contrib import admin
from adminpp import admin_models
from adminpp.filters import get_titled_filter
from post.models import Post, PostReply


# Example 1
admin_models.register_auto(admin.site, Post)
admin_models.register_auto(admin.site, PostReply)


# Example 2
class PostAdminModel(admin_models.AdminModel):
    user = admin_models.CharField(source='author')

    class Meta:
        model = Post
        search_fields = ['title', 'content']
        list_filter = [
            ('title', get_titled_filter('Post title')),
        ]
        proxy_name = 'PostProxy'

    def get_queryset(self):
        return super(PostAdminModel, self).get_queryset()


class PostReplyAdminModel(admin_models.AdminModel):
    content = admin_models.CharField()

    class Meta:
        model = PostReply
        proxy_name = 'PostReplyProxy'


admin_models.register(admin.site, PostAdminModel)
admin_models.register(admin.site, PostReplyAdminModel)
