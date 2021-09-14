from . import views

from django.conf.urls import url

app_name = "groupmanagement"

urlpatterns = [
    # groups
    url(r"^groups/$", views.groups_view, name="groups"),
    url(r"^group/request/join/(\w+)/$", views.group_request_add, name="request_add"),
    url(
        r"^group/request/leave/(\w+)/$", views.group_request_leave, name="request_leave"
    ),
    # group management
    url(r"^groupmanagement/requests/$", views.group_management, name="management"),
    url(r"^groupmanagement/membership/$", views.group_membership, name="membership"),
    url(
        r"^groupmanagement/membership/(\w+)/$",
        views.group_membership_list,
        name="membership",
    ),
    url(
        r"^groupmanagement/membership/(\w+)/audit-log/$",
        views.group_membership_audit,
        name="audit_log",
    ),
    url(
        r"^groupmanagement/membership/(\w+)/remove/(\w+)/$",
        views.group_membership_remove,
        name="membership_remove",
    ),
    url(
        r"^groupmanagement/request/join/accept/(\w+)/$",
        views.group_accept_request,
        name="accept_request",
    ),
    url(
        r"^groupmanagement/request/join/reject/(\w+)/$",
        views.group_reject_request,
        name="reject_request",
    ),
    url(
        r"^groupmanagement/request/leave/accept/(\w+)/$",
        views.group_leave_accept_request,
        name="leave_accept_request",
    ),
    url(
        r"^groupmanagement/request/leave/reject/(\w+)/$",
        views.group_leave_reject_request,
        name="leave_reject_request",
    ),
]
