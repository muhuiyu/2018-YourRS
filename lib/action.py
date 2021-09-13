# coding: utf8
import argparse, random, json, datetime
import numpy as np
from lib.parameters import *
from lib.tools import *

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
from torch.distributions import Categorical
from itertools import count
from sklearn.ensemble import RandomForestClassifier

from IPython import embed

class History(object):
    """docstring for History."""
    def __init__(self):
        super(History, self).__init__()
        self.record = []
    def contain(self, pair):
        pass

def softmax(x): return np.exp(x) / np.exp(x).sum(axis=0)
class Policy(nn.Module):
    def __init__(self, dim_out):
        super(Policy, self).__init__()
        self.affine1 = nn.Linear(DIM_STATES, 128)
        self.affine2 = nn.Linear(128, dim_out)
        self.saved_log_probs = []
        self.rewards = []
    def forward(self, x):
        x = F.relu(self.affine1(x))
        action_scores = self.affine2(x)
        return F.softmax(action_scores, dim=1)

class DialogManager(object):
    """docstring for DialogManager."""
    def __init__(self):
        super(DialogManager, self).__init__()
        self.policy = Policy(dim_out=N_ACTIONS-1)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=LEARNING_RATE)
        self.classifer = RandomForestClassifier(max_depth=10, n_estimators=10, max_features=1)
        # self.history = History()
        self.prev_action = None
        self.prev_state = None
        # self.i_episode = 0
        self.sum_reward = 0

    def feedback(self, state_, s_, parameters, turn, conflict):
        # bad feedback situations:
        #   1. ask
        #   2. no reason return answer, praise_item
        #   3. ask known infomation
        #   4. ask conflict
        # print('feedback:',state_, self.prev_state, ACTIONTABLE[self.prev_action])
        # for tag in ['item','brand','color','price']:
        #     if tag in ACTIONTABLE[self.prev_action] and self.prev_state[SLOTPARA[tag]]!=0: return R_WRONG, False, True
        if self.prev_action==RECOMMEND:
            if state_=='react' and isgood(parameters): return R_SUCCESS, True, False
            else: return R_FAIL, True, False
        elif turn==MAXTURNS: return R_NONE, True, False
        elif conflict: return R_WRONG, False, True
        elif not self.prev_state[0]==STATEDICT['greeting'] and ACTIONTABLE[self.prev_action]=='greeting': return R_WRONG, False, True
        elif not self.prev_state[0]==STATEDICT['request'] and self.prev_action==ANSWER: return R_WRONG, False, True
        else: return 0, False, False

    def update(self, state_, parameters, s_, turn, conflict):
        if self.prev_action==None:
            self.prev_state = s_
            return
        reward, done, conflict = self.feedback(state_, s_, parameters, turn, conflict)
        # print('reward: {}, done: {}, conflict: {}'.format(reward, done, conflict))
        self.policy.rewards.append(reward)
        # self.history.record.append([self.prev_action,s_])
        if done:
            if reward>0: self.policy.rewards[-1] = reward
            # print('ep %d: policy network parameters updating...' % (self.i_episode))
            self.finish_episode()
            self.clear_policy()
            self.prev_state = None
            self.prev_action = None
            return True
        else:
            self.prev_state = s_
            return False

    def action(self, db, s, turn):
        action = self.select_action(s, turn)
        if action==RECOMMEND: prediction = 1
            # if self.i_episode <= BATCH_SIZE: prediction = random.choice([0,1])
            # else: prediction = self.classifer.predict([s])
        else: prediction = -1
        self.prev_action = action
        return action, prediction

    def select_action(self, s, t):
        state = torch.from_numpy(s).float().unsqueeze(0)
        probs = self.policy(Variable(state))
        m = Categorical(probs)
        if s[0]==STATEDICT['request']: action = Variable(torch.LongTensor([ANSWER]))     # request should be responsed with answer
        elif random.random() > EPSILON: action = Variable(torch.LongTensor([random.randint(0, N_ACTIONS-2)]))
        else: action = m.sample()
        self.policy.saved_log_probs.append(m.log_prob(action))
        return action.data[0]

    def finish_episode(self):
        print('reward',self.policy.rewards)
        self.sum_reward+=sum(self.policy.rewards)
        if self.policy.rewards!=[]:
            R = 0   # policy
            policy_loss = []
            rewards = []
            for r in self.policy.rewards[::-1]:
                R = r + GAMMA * R
                rewards.insert(0, R)
            rewards = torch.Tensor(rewards)
            a = np.finfo(np.float32).eps + torch.std(rewards)
            rewards = (rewards - rewards.mean()) / a
            for log_prob, reward in zip(self.policy.saved_log_probs, rewards): policy_loss.append(-log_prob * reward)
            #embed()
            self.optimizer.zero_grad()
            policy_loss = torch.cat(policy_loss).sum()
            policy_loss.backward(retain_graph=True)
            self.optimizer.step()
        return

    def clear_policy(self):
        del self.policy.rewards[:]
        del self.policy.saved_log_probs[:]
