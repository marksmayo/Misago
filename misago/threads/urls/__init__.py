from django.urls import path

from ...conf import settings

from ..views.attachment import attachment_server
from ..views.goto import (
    ThreadGotoPostView,
    ThreadGotoLastView,
    ThreadGotoNewView,
    ThreadGotoBestAnswerView,
    ThreadGotoUnapprovedView,
    PrivateThreadGotoPostView,
    PrivateThreadGotoLastView,
    PrivateThreadGotoNewView,
)
from ..views.list import ForumThreadsList, CategoryThreadsList, PrivateThreadsList
from ..views.subscribed import redirect_subscribed_to_watched
from ..views.thread import ThreadView, PrivateThreadView

LISTS_TYPES = ("all", "my", "new", "unread", "watched", "unapproved")


def threads_list_patterns(prefix, view, patterns):
    urls = []
    for i, pattern in enumerate(patterns):
        if i > 0:
            url_name = f"{prefix}-{LISTS_TYPES[i]}"
        else:
            url_name = prefix

        urls.append(
            path(
                pattern,
                view.as_view(),
                name=url_name,
                kwargs={"list_type": LISTS_TYPES[i]},
            )
        )

    return urls


if settings.MISAGO_THREADS_ON_INDEX:
    urlpatterns = threads_list_patterns(
        "threads",
        ForumThreadsList,
        (
            "",
            "my/",
            "new/",
            "unread/",
            "watched/",
            "unapproved/",
        ),
    )
else:
    urlpatterns = threads_list_patterns(
        "threads",
        ForumThreadsList,
        (
            "threads/",
            "threads/my/",
            "threads/new/",
            "threads/unread/",
            "threads/watched/",
            "threads/unapproved/",
        ),
    )

urlpatterns += threads_list_patterns(
    "category",
    CategoryThreadsList,
    (
        "c/<slug:slug>/<int:pk>/",
        "c/<slug:slug>/<int:pk>/my/",
        "c/<slug:slug>/<int:pk>/new/",
        "c/<slug:slug>/<int:pk>/unread/",
        "c/<slug:slug>/<int:pk>/watched/",
        "c/<slug:slug>/<int:pk>/unapproved/",
    ),
)

urlpatterns += threads_list_patterns(
    "private-threads",
    PrivateThreadsList,
    (
        "private-threads/",
        "private-threads/my/",
        "private-threads/new/",
        "private-threads/unread/",
        "private-threads/watched/",
    ),
)


# Redirect from subscribed to watched
if settings.MISAGO_THREADS_ON_INDEX:
    root_subscribed_path = "subscribed/"
else:
    root_subscribed_path = "threads/subscribed/"

urlpatterns += [
    path(root_subscribed_path, redirect_subscribed_to_watched),
    path("c/<slug:slug>/<int:pk>/subscribed/", redirect_subscribed_to_watched),
    path("private-threads/subscribed/", redirect_subscribed_to_watched),
]


def thread_view_patterns(prefix, view):
    urls = [
        path(
            f"{prefix[0]}/<slug:slug>/<int:pk>/",
            view.as_view(),
            name=prefix,
        ),
        path(
            f"{prefix[0]}/<slug:slug>/<int:pk>/<int:page>/",
            view.as_view(),
            name=prefix,
        ),
    ]
    return urls


urlpatterns += thread_view_patterns("thread", ThreadView)
urlpatterns += thread_view_patterns("private-thread", PrivateThreadView)


def goto_patterns(prefix, **views):
    urls = []

    post_view = views.pop("post", None)
    if post_view:
        url_pattern = f"{prefix[0]}/<slug:slug>/<int:pk>/post/<int:post>/"
        url_name = f"{prefix}-post"
        urls.append(path(url_pattern, post_view.as_view(), name=url_name))

    for name, view in views.items():
        name = name.replace("_", "-")
        url_pattern = f"{prefix[0]}/<slug:slug>/<int:pk>/{name}/"
        url_name = f"{prefix}-{name}"
        urls.append(path(url_pattern, view.as_view(), name=url_name))

    return urls


urlpatterns += goto_patterns(
    "thread",
    post=ThreadGotoPostView,
    last=ThreadGotoLastView,
    new=ThreadGotoNewView,
    best_answer=ThreadGotoBestAnswerView,
    unapproved=ThreadGotoUnapprovedView,
)

urlpatterns += goto_patterns(
    "private-thread",
    post=PrivateThreadGotoPostView,
    last=PrivateThreadGotoLastView,
    new=PrivateThreadGotoNewView,
)

urlpatterns += [
    path(
        "a/<slug:secret>/<int:pk>/",
        attachment_server,
        name="attachment",
    ),
    path(
        "a/thumb/<slug:secret>/<int:pk>/",
        attachment_server,
        name="attachment-thumbnail",
        kwargs={"thumbnail": True},
    ),
]
