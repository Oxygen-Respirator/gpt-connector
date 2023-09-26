import json
from asgiref.sync import sync_to_async
import openai


@sync_to_async
def completion(request):
    # request 처리
    request_dict = json.loads(request)

    message = request_dict['message']
    is_first = request_dict['first']
    lang_name = request_dict['lang']

    # OpenAI API 호출을 위한 messages 생성
    messages = creat_message(lang_name, message, is_first)

    call_openai = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=messages, temperature=1,
                                               max_tokens=1024)

    # OpenAI API 호출
    completion_result = call_openai["choices"][0]["message"]["content"]

    print(completion_result)

    # OpenAI API 호출 결과를 응답 형태로 가공
    data = parse_message(completion_result)

    return json.dumps(data)


def creat_message(lang_name, message, is_first):
    messages = [{"role": "system", "content": "너는 개발자 면접관으로 10년째 일하고 있어. 오직 " + lang_name + "에 대해서만 말해."},
                {"role": "system", "content": "말투 : 친절하게, 전문적이게"}]

    if is_first:
        messages.extend([
            {"role": "system", "content": "면접 질문 내용만 말하고 수식어구 및 설명은 없애. \n - 질문 : {질문 내용}"},
            {"role": "user", "content": lang_name + "에 대한 면접 질문 한개만 말해줘"}
        ])
    else:
        messages.extend([
            {"role": "system", "content": "유저가 말하는 내용을 1점에서 100점까지 점수로 판단해야해. 문장 가장 처음은 무조건 점수부터 출력해"},
            {"role": "system", "content": "유저가 말하는 내용에 대한 점수는 데이터의 정확도로 판단해. \"모르겠음\"의 의미가 포함되면 0점이야."},
            {"role": "system", "content": "네가 판단한 점수는 오직 \"점수: N점\"이라고만 말해."},
            {"role": "system",
             "content": "유저가 말한 내용에 대해 '답변'과 '키워드'와 '꼬리질문'을 말해.\n - 답변 : {답변}\n - 키워드: {키워드}\n - 꼬리질문: {꼬리질문}"},
            {"role": "user", "content": message}
        ])

        return messages


def parse_message(completion_result):
    # 응답을 위한 값 초기화
    score = 0
    answer = None
    keyword = None
    tail_question = None
    etc = []

    # 결과 메세지 각 라인 별로 처리
    lines = completion_result.split('\n')

    for line in lines:
        if line.startswith("점수:"):
            score = line.split(":")[1].replace("점", "").strip()
        elif line.startswith("답변:") or line.startswith("질문:"):
            answer = line.split(":")[1].strip()
        elif line.startswith("키워드:"):
            keyword = line.split(":")[1].strip()
        elif line.startswith("꼬리질문:"):
            tail_question = line.split(":")[1].strip()
        else:
            etc.append(line.strip())

    # etc 를 하나의 문자 열로 합침
    etc = "\n".join(etc).strip() if etc else None

    # 가공을 마친 데이터 리턴
    return {
        'score': score,
        'answer': answer,
        'keyword': keyword,
        'tail_question': tail_question,
        'etc': etc
    }
