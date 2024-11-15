from rest_framework import viewsets
from .models import User, UserCode
from .serializers import UserSerializer, UserCodeSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Дополнительный метод для получения преподавателей
    @action(detail=False, methods=['get'])
    def teachers(self, request):
        # Получаем преподавателей
        teachers = User.objects.filter(is_admin=False)
        serializer = self.get_serializer(teachers, many=True)
        return Response(serializer.data)


class UserCodeViewSet(viewsets.ModelViewSet):
    queryset = UserCode.objects.all()
    serializer_class = UserCodeSerializer
    # Дополнительный метод для проверки кода преподавателя
    @action(detail=False, methods=['post'])
    def verify_code(self, request):
        user_id = request.data.get('user_id')
        code = int(request.data.get('code'))
        try:
            user = User.objects.get(id=user_id)
            user_code = UserCode.objects.get(user_id=user.id)
            if user_code.code == code:
                return Response({'status': 'success'})
            else:
                return Response({'status': 'invalid code'}, status=400)
        except UserCode.DoesNotExist:
            return Response({'status': 'code not found'}, status=400)
        except User.DoesNotExist:
            return Response({'status': 'user not found'}, status=400)


