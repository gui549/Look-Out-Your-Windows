from copy import deepcopy
from typing import List, Union
from numpy import divide

import torch
from torchvision.transforms.functional import to_pil_image
from PIL import Image
from torchvision import transforms

from hidt import trainers
from hidt.utils.io import get_config
from hidt.utils.preprocessing import get_transform, get_params

IMAGE_WIDTH, IMAGE_HEIGHT = 1024, 1024


class StyleTransformer:
    """
    Inference class for pretrained model.
    """

    def __init__(self,
                 config_path,
                 checkpoint_path=None,
                 inference_size=512,
                 interpolate_mode='bilinear',
                 device='cuda',
                 ):
        """
        Construct StyleTransformer

        config_path: path to model config
        checkpoint_path: path to checkpoint file
        inference_size: resolution for style inference (better use resolution used for training)
        interpolate_mode: interpolation mode for style upsampling before merging with original image
        """
        self.device = device
        self.image_transformers = dict()
        self.interpolate_mode = interpolate_mode
        self.config = get_config(config_path)

        self.trainer = getattr(trainers, self.config['trainer'])(self.config) # getattr(trainers, config[trainer]) = Trainerbase()
        if checkpoint_path is not None: # load checkpoint state dictionary
            if device == 'cpu':
                state_dict = torch.load(checkpoint_path, map_location=torch.device('cpu'))
            else:
                state_dict = torch.load(checkpoint_path)
                
            state_dict_fixed = dict()
            for key in state_dict:
                state_dict_fixed[key.replace('module.', '')] = state_dict[key]
            self.trainer.gen.load_state_dict(state_dict_fixed)
        self.trainer = self.trainer.to(torch.device(device))
        self.trainer.eval() # set to evaluation mode = training mode

        self.color_space = self.config['test_dataset']['data']['images']['color_space'] # rgb

        content_image_transform_params = self.config['test_dataset']['transform']
        content_image_transform_params['color_space'] = self.color_space
        content_image_transform_params['preprocess'] = 'scale_load_shorter_side'
        content_image_transform_params['load_size'] = inference_size
        content_image_transform_params['no_flip'] = True

        style_image_transform_params = deepcopy(content_image_transform_params) # just to be safe
        style_image_transform_params['load_size'] = inference_size # XXX: redundant?

        self.image_transformers['content'] = get_transform(get_params(content_image_transform_params,
                                                                      size=(IMAGE_WIDTH, IMAGE_HEIGHT)))

        self.image_transformers['style'] = get_transform(get_params(style_image_transform_params,
                                                                    size=(IMAGE_WIDTH, IMAGE_HEIGHT)))

        self.image_transformers['original_image'] = transforms.ToTensor()
        # get_params returns a dictionary
        # get_transforms returns a torchvision.transforms

    def preprocess_images(self, pil_image: Union[List[Image.Image], Image.Image], mode='content') -> List[torch.Tensor]:
        """
        :param pil_image: a single PIL image or a list of PIL images
        :param mode: 'content' or 'style' (influences on the applied image transformer)
        :return: list of 4D Tensor with shape B x C x H x W
        """
        assert mode in self.image_transformers, 'Wrong transform mode.'

        if not isinstance(pil_image, (list, tuple)): # check whether pil_image is list or tuple
            pil_image = [pil_image]

        output = []
        equally_sized_batch = True
        for cur_image in pil_image:
            if cur_image.size != pil_image[0].size: # size = (Height, Width)
                equally_sized_batch = False
            output.append(self.image_transformers[mode]( 
                cur_image).to(self.device)) 

        if len(output) > 1:
            if equally_sized_batch:
                return [torch.stack(output)] # B = 1, C = len(output)
            else:
                return [tensor.unsqueeze(0) for tensor in output] # B = len(output), C = 1
        else:
            return [torch.stack(output)]

    def _decomposition_computation(self, pil_image: Union[List[Image.Image], Image.Image], batch_size=None, mode='content') -> List:
        """
        :param pil_image: a single PIL image or a list of PIL images
        :param batch_size: Size of images in batch.
        :param mode: type of decomposition - content or style
        :return: list of decompositions. Batch size of decomposition elements depends on if all the images have
            equal shape
        """

        if mode == 'content':
            encoding_fn = self.trainer.gen.encode_content_batch #in "gen_contents_style_net.py"
        elif mode == 'style':
            encoding_fn = self.trainer.gen.encode_style_batch #in "gen_content_style.py"
        else:
            encoding_fn = self.trainer.gen.encode #in "gen_content_style.py"

        output = []
        with torch.no_grad():
            img_tensors = self.preprocess_images(pil_image, mode=mode) # get list of 4D Tensor with shape B x C x H x W
            for current_tensor in img_tensors: # current_tensor.shape = C X H X W
                data = dict(images=current_tensor) # data = {images : current tensor}
                current_output = encoding_fn(data, batch_size=batch_size)
                output.append(current_output)
        return output

    def get_style(self, pil_image: Union[List[Image.Image], Image.Image], batch_size=None): 
        """
        Return style tuple for pil image or list of pil images

        :param batch_size: Size of images in batch.
        :param pil_image: List of PIL images or single PIL image to extract style
        :return: tensor
        """
        return self._decomposition_computation(pil_image, batch_size=batch_size, mode='style')

    def get_content(self, pil_image: Union[List[Image.Image], Image.Image], batch_size=None):
        """
        Return content for pil image or list of pil images

        :param batch_size: Size of images in batch.
        :param pil_image: List of PIL images or single PIL image to extract content
        :return: tensor
        """
        return self._decomposition_computation(pil_image, batch_size=batch_size, mode='content')

    @torch.no_grad()
    def transfer_decompositions(self, source_decompositions, target_decompositions, batch_size=None) -> List[torch.Tensor]:
        """
        Mix decompositions and return image tensors
        :param source_decompositions: list of decompositions for content image
        :param target_decompositions: list of decompositions for style images. Batch sizes in decompositions should be
            equal to those of source_decompositions or equal to one
        :param batch_size:
        :return: list of 4D image tensors. Batch sizes of these tensors correspond to batch sizes from decompositions
        """
        image_tensors = []
        for decomposition_a, decomposition_b in zip(source_decompositions, target_decompositions): # decomposition_a, b = dictionary
            decomposition = self.trainer._mix_decompositions(   # TODO : CURRENT POINT
                decomposition_a, decomposition_b)
            tensor = self.trainer.gen.decode(
                decomposition, batch_size=batch_size)['images']
            image_tensors.append(tensor)
        return image_tensors

    def image_tensors_to_pil(self, image_tensors: List[torch.Tensor]) -> List[Image.Image]:
        """
        Use for processing transfer_decompositions method output to list of pil images.
        :param image_tensors: list of 4D image tensors, for example list batches of images.
        :return: list of pil images
        """

        images = []
        for image_batch in image_tensors:
            image_batch = image_batch * 0.5 + 0.5
            for trans_tensor in image_batch:
                images.append(to_pil_image(trans_tensor.cpu()))

        return images

    @torch.no_grad()
    def transfer_images_to_styles(self,
                                  pil_images: Union[Image.Image, List[Image.Image]],
                                  target_decompositions,
                                  batch_size=None,
                                  return_pil=True):
        """

        :param pil_images: a single PIL image or a list of them
        :param target_decompositions: list of decompositions for style images. Batch sizes in decompositions should be
            equal to the number of pil_images (if those ones have equal shapes) or to one
        :param batch_size:
        :return output:  list of lists of PIL images

            All the outputs have the following structure: output[batch_number][style_number][content_number_within_content_batch]
        """
        # list of decompositions of batches
        source_decompositions = self.get_content(
            pil_images, batch_size=batch_size) 
        #source_decompositions = [{content : a list of tensors, intermediate_outputs : a list of tensors}, ... , {}]
        output_translated = []

        # for decomposition of batch, batch of image tensors in zip(...)
        for cur_source_decomposition in source_decompositions: #cur_source_decomposition = {content : a list of tensors, intermediate_outputs : a list of tensors}
            # for target decomposition of batch
            batch_translated = []
            for cur_target_decomposition in target_decompositions:
                # calculate the translated batch (list of size 1), take it from list and rescale to [0, 1] pixel values
                translated_tensors = self.transfer_decompositions([cur_source_decomposition], 
                                                                  [cur_target_decomposition],
                                                                  batch_size=batch_size,
                                                                  )[0] * 0.5 + 0.5
                for trans_tensor in translated_tensors.unbind(0):
                    batch_translated.append(to_pil_image(trans_tensor.cpu()) if return_pil else trans_tensor)
            output_translated.append(batch_translated)

        return output_translated
