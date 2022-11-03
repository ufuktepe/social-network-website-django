
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createpost", views.create_post, name="create_post"),
    path("editpost/<int:post_id>", views.edit_post, name="edit_post"),
    path("user/<int:user_id>", views.display_profile, name="display_profile"),
    path("switchfollow/<int:other_user_id>", views.switch_follow, name="switch_follow"),
    path("switchlike/<int:post_id>", views.switch_like, name="switch_like"),
    path("following", views.display_following, name="display_following")
]
