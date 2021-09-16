class XAIDashboard:
    """
    The XAIDashboard class provides the base of the XAI template.

    It requires a PyTorch or Keras model and a zcontext object, and visualizes the provided XAI algorithms, the original image and the predicted classes within panels. It also allows for visualizing certain XAI algorithms that work on a per-layer basis (e.g. Grad-CAM) on the model itself, under the associated Conv nodes.

    Attributes:
        model (torch.nn.Module or tf.Keras.nn.Model): Model to be used for XAI algorithms as well as visualization
        zcontext (zetane.context.Context): The context object all visual elements will be sent to
        zmodel (zetane.render.model.Model): The Zetane Model (converted from the Keras/PyTorch model) to be visualized
        algorithms (list(str)): The list of XAI algorithms to be visualized
        scale_factor (int): The scaling factor to scale images appropriately in the Zetane panels.
        xai_panel (zetane.render.panel.Panel): The main panel object that houses all other panels
        org_img_panel (zetane.render.panel.Panel): Panel for visualizing the original image
        topk_panel (zetane.render.panel.Panel): Panel for visualizing the top k predictions of the model as well as the target prediction if available
        explain_panel (zetane.render.panel.Panel): Panel that visualizes all global XAI algorithms
        radio_panel (zetane.render.panel.Panel): Panel to visualize the radio buttons for toggling per-layer XAI algorithms
    """
    def __init__(self, model, zcontext):
        """

        Args:
            model (torch.nn.Module or tf.Keras.nn.Model): Model to be used for XAI algorithms and visualization
            zcontext (zetane.context.Context): The context object all visual elements will be sent to
        """
        pass
    def set_model(self, model):
        """
        Updates the model used for XAI algorithms and visualization.

        Args:
            model (torch.nn.Module or tf.Keras.nn.Model): Model to be used for XAI algorithms as well as visualization

        Returns:
            None

        """
        return self
    def set_algorithms(self, algorithms):
        """
        Updates the list of XAI algorithms to be visualized.

        Args:
            algorithms (list(str)): The list of XAI algorithms to be visualized

        Returns:
            None

        """
        return self
    def normalize(self, x):
        """
        Applies 0-1 normalization.

        Args:
            x (ndarray): The numpy array to be normalized

        Returns:
            ndarray: The normalized array

        """
        return self
    def _set_topk(self, k=5):
        """
        Sets the Zetane text objects used to display the top k class probabilities in the universe.

        Args:
            k (int): The top number of classes that is to be displayed (default: 5)

        Returns:
            None
        """
        return self
    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        return self
    def _topk(self, outputs, class_dict, label_class):
        """
        Given softmax outputs, computes the top k predictions and highlights the target class if among them.

        Args:
            outputs (ndarray): Softmax outputs
            class_dict (dict): The class dictionary for the class names
            label_class (int): Index of the target class to be highlighted

        Returns:
            None
        """
        return self
    def _build_block(self, propname, image, text="", scale=0.11):
        return self
    def _compute_xai_keras(self, prep_img, algorithms, target_class, layer_list=None, loss_fn=None, postprocess_fn=None):
        """
        Computes the XAI algorithms for the given image and list of layers using the Keras/TF framework.

        Args:
            prep_img (ndarray): The preprocessed image as numpy array
            algorithms (list(str)): The list of XAI algorithms to be visualized
            target_class (int): The output class for which the gradients will be calculated when generating the XAI images (default: None)
            layer_list (list(str)): The list of layers to apply the per layer algorithms
            loss_fn (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)
            postprocess_fn (function): Custom postprocessing function to extract class probabilities from model outputs if needed. If set to None, this defaluts to indexing into the 1D outputs array, assuming softmaxed outputs (default: None)

        Returns:
            None
        """
        return self
    def _compute_xai_torch(self, prep_img, algorithms, target_class=None, class_name=None, original_image=None, mean=None, std=None, viz_class=None, regularize=True, smooth=False):
        """
        Computes the XAI algorithms for the given image and list of layers using the PyTorch framework.

        Args:
            prep_img (ndarray): The preprocessed image as numpy array
            algorithms (list(str)): The list of XAI algorithms to be visualized
            target_class (int): The output class for which the gradients will be calculated when generating the XAI images (default: None)
            class_name (str): The name of the output class for which the XAI images are generated (default: None)
            original_image (): The original image, used for overlaying in LIME, Grad-CAM and Score-CAM (default: None)
            mean (list(float)): The mean values for each channel if any in normalization is applied to the original image (default: None)
            std (list(float)): The standard deviation values for each channel if any in normalization is applied to the original image (default: None)
            viz_class (int): The output class which the generative algorithms will use in optimization. Takes effect only if generative algorithms are called. (default: None)
            regularize (bool): Whether to apply regularization, takes effect only on algorithms that support regularization, e.g. image generation (default: True)
            smooth (bool): Whether to apply smoothing, takes effect only on algorithms that support smoothing, e.g. guided backprop (default: True)

        Returns:
            None
        """
        return self
    def _layout_xai(self):
        return self
    def explain_torch(self, img_data, target_class=None, label_class=None, class_dict=None, algorithms=None, mean=None, std=None, opset_version=12):
        """
        Runs the explainability template on a PyTorch classification model. Given an image path or data, computes the desired XAI algorithms and the top k predicted classes, and displays them along with the model and the original image.

        Args:
            img_data (str, ndarray or torch.Tensor): The input image in filepath or Numpy/torch array form
            target_class (int): The output class for which the gradients will be calculated when generating the XAI images (default: None)
            label_class (int): If available, the ground truth class label (default: None)
            class_dict (dict): The class dictionary for the class names
            algorithms (list(str)): The list of XAI algorithms to be visualized
            mean (list(float)): The mean values for each channel if any in normalization is applied to the original image (default: None)
            std (list(float)): The standard deviation values for each channel if any in normalization is applied to the original image (default: None)
            opset_version (int): ONNX opset version (default: 12)

        Returns:
            None
        """
        return self
    def explain_keras(self, img_data, target_class=None, label_class=None, class_dict=None, algorithms=None, loss_fn=None, postprocess_fn=None):
        """
        Runs the explainability template on a Keras classification model. Given an image path or data, computes the desired XAI algorithms and the top k predicted classes, and displays them along with the model and the original image.

        Args:
            img_data (str or ndarray): The input image in filepath or Numpy array form
            target_class (int): The output class for which the gradients will be calculated when generating the XAI images (default: None)
            label_class (int): If available, the ground truth class label (default: None)
            class_dict (dict): The class dictionary for the class names
            algorithms (list(str)): The list of XAI algorithms to be visualized
            loss_fn (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)
            postprocess_fn (function): Custom postprocessing function to extract class probabilities from model outputs if needed. If set to None, this defaluts to indexing into the 1D outputs array, assuming softmaxed outputs (default: None)

        Returns:
            None
        """
        return self
    def _set_notification_message(self, message: str):
        return self
    def _start_notification_border_animation(self):
        return self
    def _stop_notification_border_animation(self):
        return self
    def _delete_notification_panel(self):
        return self
    def _make_notification_panel(self):
        return self
    def _populate_xai_layer_list(self, predicate=lambda node: True):
        return self
