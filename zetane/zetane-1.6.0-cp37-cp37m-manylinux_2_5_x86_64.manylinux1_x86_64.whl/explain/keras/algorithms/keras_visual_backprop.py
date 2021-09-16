class VisualBackprop:
    """A SaliencyMask class that computes saliency masks with VisualBackprop
    """
    def __init__(self, model, output_index=0):
        """Constructs a VisualProp SaliencyMask.
        Args:
            model: Provides input model for calculating VisualBackprop
            output_index: Provides the index of the output
        """
        pass
    def get_mask(self, input_image):
        """Returns a VisualBackprop mask.
        Args:
            input_image: Provides the input image
        Returns:
        visual_bpr[0]: value at the 0th index 
        """
        return self
    def _deconv(self, feature_map):
        """The deconvolution operation to upsample the average feature map downstream
        Args:
            feature_map: Provides the feature_map
        Returns:
        deconv_func([feature_map, 0])[0]: deconvolution of the feature maps
        """
        return self
