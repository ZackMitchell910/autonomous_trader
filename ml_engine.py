import gym
import numpy as np
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from rl_env import MultiAssetTradingEnv

class MLEngine:
    def __init__(self, df, product_ids, model_save_path, algo="PPO"):
        self.df = df
        self.product_ids = product_ids
        self.model_save_path = model_save_path
        self.algo = algo

    def train_model(self, timesteps=200000):
        def make_env():
            return MultiAssetTradingEnv(self.df, self.product_ids)

        env = DummyVecEnv([make_env])

        if self.algo == "PPO":
            model = PPO("MlpPolicy", env, verbose=1)
        else:
            model = A2C("MlpPolicy", env, verbose=1)

        model.learn(total_timesteps=timesteps)
        model.save(self.model_save_path)
        return model

    def load_model(self):
        if self.algo == "PPO":
            model = PPO.load(self.model_save_path)
        else:
            model = A2C.load(self.model_save_path)
        return model

