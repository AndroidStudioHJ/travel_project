from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import cv2
import numpy as np
from .nafnet_model.basicsr.utils import img2tensor, tensor2img
from .nafnet_model.basicsr.models import create_model
from .nafnet_model.basicsr.models.archs import NAFNet_arch
import torch

def enhance_image(request):
    return render(request, 'image_enhance/enhance.html')

@csrf_exempt
def process_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Get the uploaded image
            image_file = request.FILES['image']
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the uploaded image
            input_path = os.path.join(upload_dir, 'input.jpg')
            with open(input_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            # Load and process the image
            img = cv2.imread(input_path)
            if img is None:
                raise Exception("이미지를 불러올 수 없습니다.")
            
            # BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Normalize image
            img = img.astype(np.float32) / 255.0
            
            # Convert to tensor
            img_tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
            
            # Load model and process
            model = NAFNet_arch.NAFNet(
                img_channel=3,
                width=64,
                middle_blk_num=1,
                enc_blk_nums=[1, 1, 1, 28],
                dec_blk_nums=[1, 1, 1, 1]
            )
            model.eval()
            
            # Load pretrained weights
            model_dir = os.path.dirname(os.path.abspath(__file__))
            pretrained_path = os.path.join(model_dir, 'nafnet_model', 'experiments', 'pretrained_models', 'NAFNet-REDS-width64.pth')
            
            if os.path.exists(pretrained_path):
                checkpoint = torch.load(pretrained_path, map_location='cpu')
                if 'params' in checkpoint:
                    model.load_state_dict(checkpoint['params'])
                else:
                    model.load_state_dict(checkpoint)
            else:
                raise Exception("사전 학습된 모델 파일을 찾을 수 없습니다.")
            
            # Move tensor to the same device as the model
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model = model.to(device)
            img_tensor = img_tensor.to(device)
            
            with torch.no_grad():
                output = model(img_tensor)
            
            # Convert back to image
            output = output.squeeze(0).permute(1, 2, 0).cpu().numpy()
            output = (output * 255.0).clip(0, 255).astype(np.uint8)
            
            # Save the enhanced image
            output_path = os.path.join(upload_dir, 'output.jpg')
            cv2.imwrite(output_path, cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
            
            # Return the URL of the enhanced image
            return JsonResponse({
                'success': True,
                'output_url': '/media/uploads/output.jpg'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })

def result(request):
    input_image = request.GET.get('input')
    output_image = request.GET.get('output')
    
    context = {
        'input_image': f'/media/input/{input_image}',
        'output_image': f'/media/output/{output_image}'
    }
    
    return render(request, 'image_enhance/result.html', context)
