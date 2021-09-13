from django.urls import path

from NEMO_billing import views

urlpatterns = [
    path("custom_charges/", views.custom_charges, name="custom_charges"),
    path("custom_charge/", views.create_or_modify_custom_charge, name="create_custom_charge"),
    path("custom_charge/<int:custom_charge_id>", views.create_or_modify_custom_charge, name="edit_custom_charge"),

    # Overriding NEMO create staff charge URLs to add core facility selection
    path("staff_charges/", views.custom_staff_charges, name="staff_charges"),
    path("begin_staff_charge/", views.custom_begin_staff_charge, name="begin_staff_charge"),

    # Overriding NEMO enable tool URL to set the core facility on staff charge based on the tool's core facility
    path("enable_tool/<int:tool_id>/user/<int:user_id>/project/<int:project_id>/staff_charge/<str:staff_charge>/", views.custom_enable_tool, name="enable_tool"),
]
