from django.urls import path 
from . import views, blog_group_views, post_views, category_views, comment_views

urlpatterns = [ 
    path('category/new', category_views.CreateCategoryView.as_view(), name='create_category'),
    path('category/all', category_views.ListCategoryView.as_view(), name='list_category'),
    path('group/new', blog_group_views.CreateBlogGroup.as_view(), name='create_group'),
    path('<str:ct_name>/group/all', blog_group_views.ListBlogGroupView.as_view(), name='list_group'),

    path('group/private/all', blog_group_views.PrivateListBlogGroupView.as_view(), name='private_list_groups'),
    path('group/private/<slug:slug>/detail', blog_group_views.PrivateGroupDetailView.as_view(), name='member_group'),

    #check author permission
    path('group/check/author/permission', blog_group_views.AuthorPermissionView.as_view(), name='check_author_permission'),
    path('group/check/member/permission', post_views.IsMemberPermissionView.as_view(), name='check_member_permission'),
    path('group/check/author/post/permission', post_views.IsAuthorPermissionView.as_view()),

    path('group/<slug:slug>/join', blog_group_views.JoinGroupView.as_view(), name='join_group'),
    path('group/all/joined', blog_group_views.JoinedGroupListView.as_view(), name='user_joined_group'),
    path('group/<slug:slug>/detail', blog_group_views.BlogGroupDetail.as_view(), name='blog_detail'),
    path('group/<slug:slug>/join', blog_group_views.JoinGroupView.as_view(), name='join_group'),
    path('group/<slug:slug>/permissions', blog_group_views.AssignPermissionView.as_view(), name='assign_permissions'),
    path('group/<slug:slug>/edit', blog_group_views.ManageBlogGroupView.as_view(), name='blog_edit'),
    path('group/<slug:slug>/members', blog_group_views.ListGroupMembers.as_view(), name='list_members'),
    path('group/<slug:slug>/delete', blog_group_views.ManageBlogGroupView.as_view(), name='delete_group'),

    path('<slug:blog_group>/posts/new', post_views.CreatePostView.as_view(), name='create_post'),
    path('<slug:blog_group>/posts/all', post_views.PostPublicListView.as_view()),
    path('<slug:blog_group>/posts/author/all', post_views.PostPrivateListView.as_view(), name='list_posts'),
    path('<slug:blog_group>/posts/<slug:post_slug>/detail', post_views.PostDetailPublicView.as_view()),

    path('<slug:blog_group>/posts/<slug:post_slug>/comments/new', comment_views.SubmitCommentView.as_view(), name='submit_comment'),
    path('<slug:blog_group>/posts/<slug:post_slug>/comments/all', comment_views.ListCommentView.as_view(), name='list_comments'),
    path('<slug:blog_group>/posts/<slug:post_slug>/comments/<int:comment_id>/like', comment_views.LikeCommentView.as_view(), name='like_comment'),
    path('<slug:blog_group>/posts/<slug:post_slug>/comments/<int:comment_id>/dislike', comment_views.DislikeCommentView.as_view(), name='dislike_comment'),

    path('<slug:blog_group>/posts/<slug:post_slug>/likes', post_views.LikePostView.as_view()),
    path('<slug:blog_group>/posts/<slug:post_slug>/dislikes', post_views.DisLikePostView.as_view()),
    path('<slug:blog_group>/posts/<slug:post_slug>/author/detail', post_views.PostPrivateDetailView.as_view(), name='post_detail'),
    path('<slug:blog_group>/posts/<slug:post_slug>/paragraph/add', post_views.AddParagraphView.as_view(), name='add_paragraph'),
    path('<slug:blog_group>/posts/<slug:post_slug>/paragraph/<int:para_id>/edit', post_views.EditParagraphView.as_view(), name='edit_paragraph')
]