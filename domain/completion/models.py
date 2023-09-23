from django.db import models


class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=255, unique=True)
    user_pw = models.CharField(max_length=255)
    user_nickname = models.CharField(max_length=255)
    max_answer_count = models.IntegerField(null=True, blank=True)
    remain_answer_count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'users'


class LangGroup(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'lang_group'


class ChatMessage(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_message = models.TextField(null=True)
    score = models.IntegerField(null=True, blank=True)
    answer = models.TextField(null=True)
    keyword = models.CharField(null=True, max_length=255)
    tail_question = models.TextField(null=True)
    etc = models.TextField(null=True)
    is_resolve = models.BooleanField(null=True, blank=True)
    lang_group_id = models.BigIntegerField(null=True, blank=True)
    users_id = models.BigIntegerField(Users, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'chat_message'
