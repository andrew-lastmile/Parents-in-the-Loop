from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .llm_service import LLMService
from rest_framework import status
from .models import Document
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})

@api_view(['POST'])
@csrf_exempt
def chat_with_ai(request):
    llm_service = LLMService()
    
    message = request.data.get('message', '')
    conversation_history = request.data.get('conversation_history', [])
    
    if not message:
        return Response({"error": "Message is required"}, status=400)
    
    try:
        response = llm_service.chat_with_ai(message, conversation_history)
        return Response({"response": response})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def upload_document(request):
    logger.info("Received upload request")
    logger.info(f"Request FILES: {request.FILES}")
    logger.info(f"Request DATA: {request.data}")
    
    if 'file' not in request.FILES:
        logger.error("No file provided in request")
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    name = request.data.get('name', file.name)
    doc_type = request.data.get('type', 'Unknown')
    
    logger.info(f"Processing file: {name}, type: {doc_type}")
    
    try:
        # Save the file
        document = Document.objects.create(
            file=file,
            name=name,
            type=doc_type,
            status='processed'
        )
        
        logger.info(f"File saved successfully with ID: {document.id}")
        
        return Response({
            'id': document.id,
            'name': document.name,
            'type': document.type,
            'status': document.status,
            'upload_date': document.upload_date
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
