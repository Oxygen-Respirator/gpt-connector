from rest_framework.decorators import api_view


@api_view(['GET'])
def healthCheck(request):
    return "Success"
