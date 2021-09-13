import gym
import numpy as np
import os
import torch

from reprise.action_inference import ActionInference
from reprise.context_inference import ContextInference
from reprise.gym.rocketball.agent import Agent

from .model import LSTM


TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))

context_size = 3
action_size = 4
output_size = 2
input_size = context_size + action_size + output_size
hidden_size = 8
ai_horizon = 10
criterion = torch.nn.MSELoss()


def ci_loss(outputs, targets):
    return criterion(torch.cat(outputs, dim=0),
                     torch.cat(targets, dim=0))


def ai_loss(outputs, targets):
    return criterion(torch.cumsum(
        torch.cat(outputs, dim=0), dim=0), targets)


def test_reprise():
    np.random.seed(123)
    torch.manual_seed(123)

    model = LSTM(input_size, hidden_size, 1, output_size)
    lstm_h = torch.zeros(1, 1, hidden_size)
    lstm_c = torch.zeros(1, 1, hidden_size)
    lstm_state = [lstm_h, lstm_c]
    lstm_state_ci = [lstm_h.clone(), lstm_c.clone()]

    policy = torch.rand([ai_horizon, 1, action_size])
    optimizer = torch.optim.Adam(
        [policy], lr=0.1, betas=(0.9, 0.999))
    ai = ActionInference(
        model=model,
        policy=policy,
        optimizer=optimizer,
        inference_cycles=3,
        criterion=ai_loss,
        reset_optimizer=False,
        policy_handler=lambda x: x)

    context = torch.zeros([1, 1, context_size])
    def opt_accessor(state): return [state[0], state[1]]
    params = [{'params': [context], 'lr': 0.1},
              {'params': opt_accessor(lstm_state)}]
    optimizer = torch.optim.Adam(params)
    ci = ContextInference(
        model=model,
        initial_model_state=lstm_state_ci,
        context=context,
        optimizer=optimizer,
        inference_length=5,
        inference_cycles=5,
        criterion=ci_loss,
        reset_optimizer=False,
        opt_accessor=opt_accessor,
        context_handler=lambda x: x)

    position = torch.Tensor([[[0, 1]]])
    targets = torch.cat(
        ai_horizon *
        [torch.Tensor(
             [[np.random.uniform(-1.5, 1.5),
               np.random.uniform(0, 2)]])])
    targets = targets[:, None, :]
    delta = torch.zeros([1, 1, 2])

    env = gym.make('reprise.gym:rocketball-v0')
    env.reset()
    agent = Agent(id='foo', mode=0, init_pos=np.array([0, 1]), color='black')
    agent.update_target(targets[0][0].numpy())
    env.add_agent(agent)

    action = torch.zeros([4])

    all_actions = []
    all_contexts = []

    for t in range(50):
        observation = env.step([action.numpy()])
        position_old = position.clone()
        position = torch.Tensor(observation[0][0][1])
        position = position[None, None, :]
        delta_old = delta.clone()
        delta = position - position_old

        x_t = torch.zeros([1, 1, input_size])
        x_t[0, 0, :context_size] = context.detach()
        x_t[0, 0, context_size:context_size + action_size] = action
        x_t[0, 0, -output_size:] = delta_old

        with torch.no_grad():
            y_t, lstm_state = model.forward(x_t, lstm_state)
        context, _, states = ci.infer_contexts(
            x_t[:, :, context_size:], delta)
        lstm_state = (
            states[-1][0].clone().detach(),
            states[-1][1].clone().detach())
        policy, _, _ = ai.infer_actions(
            delta, lstm_state, context.clone().detach().repeat(
                policy.shape[0], 1, 1), targets - position)
        action = policy[0][0].detach()

        all_contexts.append(context.detach())
        all_actions.append(action.detach())

    contexts_file = os.path.join(TEST_ROOT, 'references/test_reprise_contexts.npy')
    actions_file = os.path.join(TEST_ROOT, 'references/test_reprise_actions.npy')

    contexts_ref = np.load(open(contexts_file, 'rb'))
    actions_ref = np.load(open(actions_file, 'rb'))

    assert np.allclose(contexts_ref, torch.stack(all_contexts, dim=0).numpy(), rtol=1e-04)
    assert np.allclose(actions_ref, torch.stack(all_actions, dim=0).numpy(), rtol=1e-04)
