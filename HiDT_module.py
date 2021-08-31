import glob
import os.path
from os import environ

import torch
from torchvision import transforms

from hidt.networks.enhancement.RRDBNet_arch import RRDBNet
from hidt.style_transformer import StyleTransformer
from hidt.utils.preprocessing import GridCrop, enhancement_preprocessing
from hidt.utils.io import save_img, extract_images


def infer(data_dir, style_dir, cfg_path, weight_path, enh_weights_path,
            enhancement='generator', inference_size=256, device='cpu', batch_size=1, output_dir='.'):

    if device == 'cpu':
        # Set the maximum number of threads
        os.environ["OMP_NUM_THREADS"] = "1"

    style_transformer = StyleTransformer(cfg_path, weight_path,
                                         inference_size=inference_size,
                                         device=device)

    result_path = output_dir
    # os.makedirs(result_path, exist_ok=True)  # exist_ok == False : error when target directory exists
    print("result path : ", result_path)

    source_images_path = [data_dir]
    style_images_path = glob.glob(os.path.join(style_dir, '*'))
    style_images_path = [path.replace("\\", "/") for path in style_images_path]
    # glob.glob returns a list of all files/directories matching "arg.data_dir/*"

    source_images_pil = extract_images(source_images_path) # input : [paths], output : [RGB_img]
    style_images_pil = extract_images(style_images_path)
    # returns list of PIL images
    
    with torch.no_grad():
        # RRDBNet makes resolution 4 times higher (w,h) -> (4w, 4h)
        g_enh = RRDBNet(in_nc=48, out_nc=3, nf=64, nb=5, gc=32).to(torch.device(device))
        g_enh.load_state_dict(torch.load(enh_weights_path))

        # Make 4 sub-copies of original image (==> 4 diffrent coords high-resoulution images)
        crop_transform = GridCrop(4, 1, hires_size=inference_size * 4)
        
        source_name = source_images_path[0].split('/')[-1].split('.')[0]

        for i, style_img_pil in enumerate(style_images_pil): # list of style tensors
            styles_decomposition = style_transformer.get_style([style_img_pil]) # styles_decomposition = [{"style" : * X 1 X 1 style tensor}]

            if enhancement == 'generator':  
                style = styles_decomposition[0]
                source_image = source_images_pil[0]
                
                crops = [img for img in crop_transform(source_image)]
                out = style_transformer.transfer_images_to_styles(crops, [style], batch_size=batch_size, return_pil=False) # TODO : Current Point
                padded_stack = enhancement_preprocessing(out[0])
                out = g_enh(padded_stack)
                styled_img = [transforms.ToPILImage()((out[0].cpu().clamp(-1, 1) + 1.) / 2.)]
                
                style_name = style_images_path[i].split('/')[-1].split('.')[0]
                save_img(styled_img[0], 
                        os.path.join(result_path,
                                        source_name + '_to_' + style_name + '.jpg')
                        )

            elif enhancement == 'fullconv':
                result_images = []
                for style in styles_decomposition:
                    one_style_out = style_transformer.transfer_images_to_styles(source_images_pil,
                                                                                [style],
                                                                                batch_size=batch_size,
                                                                                return_pil=True)
                    result_images.append(one_style_out)
        
        
# To test infer
if __name__ == '__main__': 
    infer(data_dir="./Test1.jpg", style_dir="./images/styles/", \
                cfg_path="./configs/daytime.yaml", \
                weight_path="./trained_models/generator/daytime.pt", \
                enh_weights_path="./trained_models/enhancer/enhancer.pth", \
                inference_size=512, \
                output_dir=".")