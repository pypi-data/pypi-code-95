"""
Action inference as part of REPRISE.

This module provides the functionality to infer actions.

"""

import torch


class ActionInference():
    """
    Action inference class.

    An instance of this class provides the functionality to infer actions.

    Parameters
    ----------
    model : torch.nn.Module
        Recurrent neural network model which might be pretrained.
    policy : torch.Tensor of shape (inference_len, batch, action_size)
        Initial policy consisting of actions. It determines the inference
        length, i.e. how far the model will predict into the future.
    criterion : function
        Criterion for comparison of a list of predictions and a target of shape
        (target_len, batch, observation_size), where target_len must be less or
        equal to inference_len. The target will be right-aligned for
        comparison, i.e. the first inference_len - target_len predictions will
        be ignored.
    optimizer : torch.optim.Optimizer
        Optimizer to optimize the policy with.
    reset_optimizer : bool
        If True the optimizer's statistics are reset before each inference.
        If False the optimizer's statistics are kept across inferences.
    inference_cycles : int
        Number of inference cycles, i.e. how often inference is repeated.
    policy_handler : function
        Function that is applied to the policy after each optimization,
        e.g. can be used to keep policy in certain range by clamping.
    output_handler : function
        Function that is applied to the output during prediction before it is
        concatenated with the policy to be fed back into the model.

    """

    def __init__(self, model, policy, criterion, optimizer,
                 reset_optimizer=True, inference_cycles=10,
                 policy_handler=lambda x: x, output_handler=lambda x: x):

        assert (len(policy.shape) ==
                3), "policy should be of shape (seq_len, batch, input_size)"
        assert (policy.size(1) == 1), "batch of policy should be 1"

        self._model = model
        self._policy = policy
        self._policy.requires_grad = True
        self._criterion = criterion
        self._optimizer = optimizer
        self._reset_optimizer = reset_optimizer
        self._inference_cycles = inference_cycles
        self._policy_handler = policy_handler
        self._output_handler = output_handler

        if self._reset_optimizer:
            self._optimizer_orig_state = optimizer.state_dict()

    def predict(self, x, state, context):
        """
        Predict into future.

        Predict observations given the current policy as well as an initial
        input and hidden state, and a context.

        Parameters
        ----------
        x : torch.Tensor
            Initial input.
        state : torch.Tensor or tuple
            Initial hidden (and cell) state of the network.
        context : torch.Tensor
            Context activations over the whole prediction.

        Returns
        -------
        outputs : list
            Result of the prediction.
        states : list of torch.Tensor or list of tuple
            Hidden (and cell) states of the model corresponding to the
            predicted outputs.

        """

        outputs = []
        states = []
        # Forward pass over policy
        for t in range(self._policy.size(0)):
            inp = torch.cat((context[t:t+1], self._policy[t:t+1], x), dim=2)
            x, state = self._model.forward(inp, state)
            outputs.append(x)
            states.append(state)
            x = self._output_handler(x)
        return outputs, states

    def infer_actions(self, x, state, context, target):
        """
        Optimize the current policy.

        Given an initial input, an initial hidden state, a context, and a
        target, this method infers a policy based on an imagination into the
        future.

        Parameters
        ----------
        x : torch.Tensor
            Initial input.
        state : torch.Tensor or tuple
            Initial hidden (and cell) state of the network.
        context : torch.Tensor
            Context activations over the whole prediction.
        target
            Target to compare prediction to.

        Returns
        -------
        policy : torch.Tensor
            Optimized policy.
        outputs : list
            Predicted observations corresponding to the optimized policy.
        states : list of torch.Tensor or list of tuple
            Hidden states of the model corresponding to the outputs.

        """

        assert (len(x.shape) ==
                3), "x should be of shape (seq_len, batch, input_size)"
        assert (x.size(0) == 1), "seq_len of x should be 1"
        assert (x.size(1) == 1), "batch of x should be 1"

        assert (len(context.shape) ==
                3), "context should be of shape (seq_len, batch, context_size)"
        assert (context.size(0) == self._policy.size(
            0)), "seq_len of context should be seq_len of policy"
        assert (context.size(1) == 1), "batch of context_size should be 1"

        assert (len(target.shape) ==
                3), "target should be of shape (seq_len, batch, output_size)"
        assert (target.size(0) <= self._policy.size(
            0)), "seq_len of target should be less than or equal to seq_len of policy"
        assert (target.size(1) == 1), "batch of target should be 1"

        if self._reset_optimizer:
            self._optimizer.load_state_dict(self._optimizer_orig_state)

        # Perform action inference cycles
        for _ in range(self._inference_cycles):
            self._optimizer.zero_grad()

            # Forward pass
            outputs, _ = self.predict(x, state, context)

            # Compute loss
            start = len(self._policy) - len(target)
            loss = self._criterion(outputs[start:], target)

            # Backward pass
            loss.backward()
            self._optimizer.step()

            # Operations on the data are not tracked
            self._policy.data = self._policy_handler(self._policy.data)

        # Policy have been optimized; this optimized policy is now propagated
        # once more in forward direction in order to generate the final output
        # to be returned
        with torch.no_grad():
            outputs, states = self.predict(x, state, context)

        # Save optimized policy to return
        policy = self._policy.clone()

        # Shift policy, last entry is duplicated
        with torch.no_grad():
            self._policy[:-1] = self._policy[1:].clone()

        return policy, outputs, states
