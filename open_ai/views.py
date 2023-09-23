from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

import openai
import json
from common.kafka import message_queue


@api_view(['POST'])
def completion(request):
    answer = request.data['message']

    messages = [
        {"role": "system", "content": "너는 개발자 면접관으로 10년째 일하고 있어. 오직 Java에 대해서만 말해."},
        {"role": "system", "content": "유저가 말하는 내용을 1점에서 100점까지 점수로 판단해야해. 문장 가장 처음은 무조건 점수부터 출력해"},
        {"role": "system", "content": "유저가 말하는 내용에 대한 점수는 데이터의 정확도로 판단해. \"모르겠음\"의 의미가 포함되면 0점이야."},
        {"role": "system", "content": "네가 판단한 점수는 오직 \"점수: N점\"이라고만 말해."},
        {"role": "system", "content": "유저가 말한 내용에 대한 공부 키워드와 꼬리질문을 말해."},
        {"role": "system", "content": "말투 : 친절하게, 전문적이게"},
        {"role": "user", "content": answer}
    ]

    call_openai = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages, temperature=0,
                                               max_tokens=2048)

    result = call_openai["choices"][0]["message"]["content"]

    kafka = message_queue.Kafka()

    kafka.setup_producer()
    kafka.produce_message('', result)

    return Response({"message": result})
