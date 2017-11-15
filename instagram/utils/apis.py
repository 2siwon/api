from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sdk.api.message import Message
"""
class SMSSerializer:
    receiver에 휴대전화 형식의 데이터가 왔는지 validate
    message에 90자 이하의 문자열이 왔는지 validate
    
    is_valid()검사 후
        serializer.data 에 있는 내용을 이용해서 send 처리
"""


class SendSMS(APIView):
    def post(self, request):
        api_key = "NCSGLMHSQ2FTVZUA"
        api_secret = "2ZNM5ZPZR07QHSLHVIFAH3XZR1GAGM2F"

        # receiver, message키로 데이터 전송
        # receiver의 번호로 message내용을 문자보내기
        # Response에는 메시지 없이 status 200 리턴

        # /api/utils/sms/send/ 로 연결
        receiver = request.data['receiver']
        message = request.data['message']

        params = dict()
        params['to'] = receiver
        params['from'] = '01029953874'
        params['text'] = message

        cool = Message(api_key, api_secret)
        if cool.send(params):
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)