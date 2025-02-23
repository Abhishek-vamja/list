from django.urls import path
from .views import add_module, delete_record, module_list, module_detail_ajax, save_record

urlpatterns = [
    path("", module_list, name="module_list"),
    path("module/<int:module_id>/ajax/", module_detail_ajax, name="module_detail_ajax"),
    path("record/<int:record_id>/delete/", delete_record, name="delete_record"),
    path("module/<int:module_id>/save/", save_record, name="save_record"),
    path("module/<int:module_id>/delete/<int:record_id>/", delete_record, name="delete_record"),
    path("module/add/", add_module, name="add_module"),
]
