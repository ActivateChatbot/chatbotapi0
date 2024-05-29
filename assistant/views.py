from django.shortcuts import render
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer,RegisterSerializer, MessageSerializer, SendMessageSerializer
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema

from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes

from .assistant import QAAssistant
from .models import ChatGptBot
from .utils import get_tokens_for_user


qa_assistant = QAAssistant()

# Class based view to Get User Details using Token Authentication
class UserDetailAPI(APIView):
  authentication_classes = (TokenAuthentication,)
  permission_classes = (AllowAny, IsAuthenticated)

  def get(self,request,*args,**kwargs):
    print(request.user)
    user = User.objects.get(id=request.user.id)
    serializer = UserSerializer(user)
    return Response(serializer.data)

#Class based view to register user
class RegisterUserAPIView(generics.CreateAPIView):
  permission_classes = (AllowAny,)
  serializer_class = RegisterSerializer

#Class based view to authenticate user
class LoginView(APIView):
    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)  # noqa: E501
        
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)

        print(username, password)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(user)
            return Response({'msg': 'Login Success', **auth_data}, status=status.HTTP_200_OK)  # noqa: E501
        return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)  # noqa: E501
    
class UserMessageView(APIView):
  authentication_classes = (TokenAuthentication,)
  permission_classes = (AllowAny, IsAuthenticated)

  def get(self, request, *args, **kwargs):
    history = ChatGptBot.objects.filter(user=request.user)
    serializer = MessageSerializer(history, many=True)
    return Response(serializer.data)
  
  
  def post(self, request, *args, **kwargs):
  
    user_input = request.POST['user_input']

    #clean input from any white spaces
    clean_user_input = str(user_input).strip()
    #send request with user's prompt
   
    if user_input:
      assistant_response = qa_assistant.run_assistant(clean_user_input)
      #bot_response = get_bot_response(user, clean_user_input)
      obj, created = ChatGptBot.objects.get_or_create(
          user=request.user,
          messageInput=clean_user_input,
          bot_response=assistant_response,
      )

      return JsonResponse({"bot_response": assistant_response})
    
    else:
        
        return JsonResponse({"error": "Please add an message"}, status=status.HTTP_400_BAD_REQUEST)
    


def convert_messages(messages):
    messages_list = []

    for message in messages:
        messages_list.append({"role": "user", "content":message['messageInput']})
        messages_list.append({"role": "assistant", "content": message['bot_response']})

    return messages_list

def get_bot_response(user, message):
    history = ChatGptBot.objects.filter(user=user).values()
    messages = convert_messages(history)
    messages.append({"role": "user", "content": message})

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
    )

    chat_message = response.choices[0].message.content
    print("Bot: ", chat_message)

    return chat_message


@csrf_exempt
@swagger_auto_schema(methods=['post'], request_body=SendMessageSerializer)
@api_view(['POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def send_message(request):

    user = request.user

    if user.is_authenticated:
        if request.method == "POST":
            user_input = request.POST['user_input']

            #clean input from any white spaces
            clean_user_input = str(user_input).strip()
            #send request with user's prompt
            """response = openai.Completion.create(
                model="text-davinci-003",
                    prompt=clean_user_input,
                    temperature=0,
                    max_tokens=1000,
                    top_p=1,
                    frequency_penalty=0.5,
                    presence_penalty=0
                    )
            
            #get response
            bot_response = response['choices'][0]['text']
            """

            if user_input:
              assistant_response = qa_assistant.run_assistant(clean_user_input)
              #bot_response = get_bot_response(user, clean_user_input)
              obj, created = ChatGptBot.objects.get_or_create(
                  user=request.user,
                  messageInput=clean_user_input,
                  bot_response=assistant_response,
              )

              return JsonResponse({"bot_response": assistant_response})
            
            else:
               
               return JsonResponse({"error": "Please add an message"}, status=status.HTTP_400_BAD_REQUEST)