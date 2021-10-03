import numpy as np
import tensorflow as tf
from tf_agents.environments import py_environment, tf_py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.utils import nest_utils

from server.const import Const
from server.game import Game
from server.kago import Kago


class DQN(Kago):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'dqn'


# シミュレータクラスの設定
class Env(py_environment.PyEnvironment):
    def __init__(self):
        super(Env, self).__init__()
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(34, 4, 17), dtype=np.float32, minimum=0, maximum=1
        )
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=33
        )
        self.count = 0
        self.stats = [0] * 4

        self._reset()

    def observation_spec(self):
        return self._observation_spec

    def action_spec(self):
        return self._action_spec

    # 初期化
    def _reset(self):
        print(self.count, '試合目')
        self.count += 1

        self.game = Game()
        self.player = DQN(id=0, game=self.game)
        self.game.start_game(player=self.player)
        self.game.start_kyoku()

        self.reward = 0
        self.game_end = False

        while self.game.next():
            pass

        time_step = ts.restart(self.board())
        return nest_utils.batch_nested_array(time_step)

    # 行動による状態変化
    def _step(self, action):
        action = nest_utils.unbatch_nested_array(action)
        score = self.score()
        dahai = self.dahai(action)
        # print(action, dahai, self.player.tehai)

        self.reward = 0
        self.game.dahai(dahai, self.player)
        while self.game.next():
            pass

        if self.game.state in [Const.RYUKYOKU_STATE, Const.AGARI_STATE]:
            self.reward = self.score() - score
            self.game_end = True
            time_step = ts.termination(self.board(), reward=0)
        elif self.game.state == Const.SYUKYOKU_STATE:
            self.reward = [90, 45, 0, -180][self.rank()] * 1000
            self.game_end = True
            time_step = ts.termination(self.board(), reward=0)
        else:
            time_step = ts.transition(self.board(), reward=0, discount=1)

        return nest_utils.batch_nested_array(time_step)

    def board(self):
        return self.player.make_input().reshape(34, 4, 17)

    def score(self):
        return self.game.scores[self.player.position]

    def dahai(self, action):
        for p in self.player.tehai:
            if p // 4 == action and self.player.can_dahai(p):
                return p

        return None

    def rank(self):
        myscore = self.game.scores[self.player.position]
        scores = sorted(self.game.scores, reverse=True)
        self.stats[scores.index(myscore)] += 1
        print(scores, myscore, scores.index(myscore))
        return scores.index(myscore)

    def random_action(self):
        return self.player.decide_dahai() // 4

    @property
    def batched(self):
        return True

    @property
    def batch_size(self):
        return 1


def main():
    print(' === MAIN ===')

    # 環境の設定
    env_py = Env()
    env = tf_py_environment.TFPyEnvironment(env_py)
    print(' === ENV LOADED === ')

    # 行動の設定
    policy = tf.compat.v2.saved_model.load('policy_1000')
    print(' === POLICY LOADED === ')

    # 学習
    num_episodes = 1000

    for episode in range(1, num_episodes + 1):
        env.reset()
        while not env.game_end:
            current_time_step = env.current_time_step()
            policy_step = policy.action(current_time_step)
            action_step = policy_step.action
            dahai = action_step.numpy()[0]
            print(dahai)
            for i in range(4):
                if env.player.can_dahai(dahai * 4 + i):
                    env.step(dahai)
                    print("ACTION")
                    break
            else:
                dahai
                env.step(env.random_action())
                print("FUCK")

        print(env.stats)

        # 学習の進捗表示 (100エピソードごと)
        if episode % 100 == 0:
            print('==== Episode {}: rank: {} ===='.format(
                episode, env.stats
            ))


if __name__ == "__main__":
    main()
