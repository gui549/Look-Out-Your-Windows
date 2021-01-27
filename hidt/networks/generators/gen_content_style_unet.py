__all__ = ['GeneratorContentStyleUnet']

from collections import defaultdict

import torch

from hidt.networks.generators import GeneratorContentStyle


class GeneratorContentStyleUnet(GeneratorContentStyle):
    def encode_content(self, data, batch_size=None):
        contents = []
        intermediate_outputs = []

        content_outputs = self.content_encoder(data)
        contents.append(content_outputs[0])
        intermediate_outputs.append(content_outputs[1:])

        return dict(
            content=torch.cat(contents),
            intermediate_outputs=[torch.cat(out) for out in zip(*intermediate_outputs)]
        )

    def encode_content_batch(self, data, batch_size=None):
        contents = []
        intermediate_outputs = []
        if batch_size is None:
            batch_size = data['images'].shape[0] # data['images'] = tensor with C X H X W

        if isinstance(batch_size, torch.TensorType):
            batch_size = batch_size.item() # when batch_size is tensor

        for images in data['images'].split(int(batch_size)): # images = batch_size X H X W 
            content_outputs = self.content_encoder(images) # content_outputs = ContentEncoderUnet(images) : encoded tensor
            contents.append(content_outputs[0]) # content_output : twice downsampled tensor
            intermediate_outputs.append(content_outputs[1:]) # intermediate output for skip connections => outputs[0] = 2 X * X * X *

        return dict(
            content=torch.cat(contents),
            intermediate_outputs=[torch.cat(out) for out in zip(*intermediate_outputs)]
        )

    def decode(self, decomposition, batch_size=None, pure_generation=False):
        if batch_size is None:
            batch_size = decomposition['content'].shape[0]
        output_maps = defaultdict(list)

        cur_content_inputs = [decomposition['content']] + list(decomposition['intermediate_outputs'])
        cur_tensor = self.decoder(cur_content_inputs, decomposition['style'], pure_generation=pure_generation)
        cur_maps = self._split_decoded_tensor_to_maps(cur_tensor)
        for map_name, map_value in cur_maps.items():
            output_maps[map_name].append(map_value)

        output_maps = {map_name: torch.cat(map_value) for map_name, map_value in output_maps.items()}
        return output_maps
