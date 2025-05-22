import sys
import os
# 프로젝트 루트 경로를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from image_enhance.nafnet_model.basicsr.models import create_model
from image_enhance.nafnet_model.basicsr.train import parse_options
from image_enhance.nafnet_model.basicsr.utils import FileClient, imfrombytes, img2tensor, tensor2img

def nafnet_enhance(input_path, output_path, options_path):
    opt = parse_options(is_train=False, options_path=options_path)
    opt['num_gpu'] = 0
    opt['dist'] = False
    opt['img_path'] = {'input_img': input_path, 'output_img': output_path}

    file_client = FileClient('disk')
    img_bytes = file_client.get(input_path, None)
    img = imfrombytes(img_bytes, float32=True)
    img = img2tensor(img, bgr2rgb=True, float32=True)
    model = create_model(opt)
    model.feed_data(data={'lq': img.unsqueeze(dim=0)})
    model.test()
    visuals = model.get_current_visuals()
    sr_img = tensor2img([visuals['result']])
    from image_enhance.nafnet_model.basicsr.utils import imwrite
    imwrite(sr_img, output_path)
    return output_path
