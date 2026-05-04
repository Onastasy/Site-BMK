from django.urls import path
from . import views
app_name = "messaging"
urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("send/", views.send_message, name="send"),
    path("chats/", views.chat_list, name="chat_list"),
    path("chats/create/", views.create_chat_room, name="create_chat"),
    path("chats/<int:chat_id>/", views.chat_room, name="chat_room"),
    path("chats/<int:chat_id>/send/", views.send_chat_message, name="send_chat_message"),
    path("chats/<int:chat_id>/messages/", views.get_chat_messages, name="get_chat_messages"),
    path("chats/<int:chat_id>/members/", views.chat_members, name="chat_members"),
    path("chats/<int:chat_id>/search/", views.search_messages, name="search_messages"),
    path("chats/<int:chat_id>/pin/<int:message_id>/", views.pin_message, name="pin_message"),
]