import json
from collections import defaultdict
from django.http import HttpResponseServerError as Http500Error
from asgiref.sync import sync_to_async
import openai

from domain.completion.models import LangGroup
from domain.completion.serializer import ChatMessageSerializer


@sync_to_async
def completion(request):
    request_dict = json.loads(request)

    user_id = request_dict['userId']
    lang_group_id = request_dict['lang']
    lang_name = LangGroup.objects.get(id=lang_group_id).name

    message = request_dict['message']

    messages = [
        {"role": "system", "content": "너는 개발자 면접관으로 10년째 일하고 있어. 오직 " + lang_name + "에 대해서만 말해."},
        {"role": "system", "content": "유저가 말하는 내용을 1점에서 100점까지 점수로 판단해야해. 문장 가장 처음은 무조건 점수부터 출력해"},
        {"role": "system", "content": "유저가 말하는 내용에 대한 점수는 데이터의 정확도로 판단해. \"모르겠음\"의 의미가 포함되면 0점이야."},
        {"role": "system", "content": "네가 판단한 점수는 오직 \"점수: N점\"이라고만 말해."},
        {"role": "system",
         "content": "유저가 말한 내용에 대해 '답변'과 '키워드'와 '꼬리질문'을 말해.\n - 답변 : {답변}\n - 키워드: {키워드}\n - 꼬리질문: {꼬리질문}"},
        {"role": "system", "content": "말투 : 친절하게, 전문적이게"},
        {"role": "user", "content": message}
    ]

    call_openai = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages, temperature=0,
                                               max_tokens=2048)

    completion_result = call_openai["choices"][0]["message"]["content"]

    print(completion_result)

    # 초기화
    score = None
    answer = None
    keyword = None
    tail_question = None
    etc = []

    # 각 라인별로 처리
    lines = completion_result.split('\n')

    for line in lines:
        if line.startswith("점수:"):
            score = line.split(":")[1].replace("점", "").strip()
        elif line.startswith("답변:"):
            answer = line.split(":")[1].strip()
        elif line.startswith("키워드:"):
            keyword = line.split(":")[1].strip()
        elif line.startswith("꼬리질문:"):
            tail_question = line.split(":")[1].strip()
        else:
            etc.append(line.strip())

    # etc를 하나의 문자열로 합침
    etc = "\n".join(etc).strip() if etc else None

    # 결과값
    data = {
        'users_id': user_id,
        'lang_group_id': lang_group_id,
        'score': score,
        'answer': answer,
        'keyword': keyword,
        'tail_question': tail_question,
        'etc': etc
    }

    # DB에 저장
    serializer = ChatMessageSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)

    del data['users_id']
    del data['lang_group_id']

    return json.dumps(data)


def count_examples():
    data_path = "question_chat_find_tuning.jsonl"

    # Load the dataset
    with open(data_path, 'r', encoding='utf-8') as f:
        dataset = [json.loads(line) for line in f]

    # Initial dataset stats
    return {"Num examples:", len(dataset)}


def jsonl_format_error_check():
    dataset = count_examples

    format_errors = defaultdict(int)

    for ex in dataset:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(k not in ("role", "content", "name") for k in message):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in ("system", "user", "assistant"):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            if not content or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            format_errors["example_missing_assistant_message"] += 1

    if format_errors:
        print("Found errors:")
        for k, v in format_errors.items():
            print(f"{k}: {v}")

        raise Http500Error("Jsonl Format")
    else:
        print("No errors found")
