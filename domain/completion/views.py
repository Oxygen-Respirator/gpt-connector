from rest_framework import viewsets
from domain.completion.models import ChatMessage, LangGroup
from domain.completion.serializer import ChatMessageSerializer


class LangGroupViewSet(viewsets.ModelViewSet):

    def get_one_lang_group_name(self, lang_group_id=1):
        return LangGroup.objects.get(id=lang_group_id).name


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(force_insert=True)
