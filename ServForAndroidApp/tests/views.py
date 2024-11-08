from .models import Test, TestResults
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import TestImageSerializer, TestResultsSerializer, TestSerializer
from .scan import scan

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class TestResultsViewSet(viewsets.ModelViewSet):
    queryset = TestResults.objects.all()
    serializer_class = TestResultsSerializer


class TestImageViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TestImageSerializer(data=request.data)
        if serializer.is_valid():
            # Передаем изображение в функцию `scan`
            processed_image_io = scan(request.FILES['image'])

            # Возвращаем обновленное изображение в ответе
            return Response(
                processed_image_io.getvalue(),
                content_type="image/jpeg",
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)