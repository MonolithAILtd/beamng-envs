import abc
from typing import Dict, Any, Iterable, Tuple, Optional, List

from gym import Space

from beamng_envs.envs.base.default_config import DefaultConfig


class IEnv(abc.ABC):
    """
    Environment interface.

    Loosely based on OpenAI gym environment wrapper, with an added run method for executing all steps in one call. This
    can be used for environments that don't require external agent interaction via an action space, although these can
    still be used with .step if implemented by the environment.

    Along with the abstract methods, the attributes should be used as defined here.

    Class attributes:
     - param_space: The full parameter/design space for the environment. Should be an OpenAI gym observation space.
     - observation_space: The observation space for the environment. Should be an OpenAI gym observation space.
     - action_space: The action space, if the environment supports agent interaction. Should be an OpenAI gym action
                     space.

    Instance attributes:
     - config: A dict containing the static config for the environment, set on init.
     - params: A dict The individual set of experimental params currently in use, set on init.
     - history: A dict containing per-step history recorded by the environment (if any).
     - results: A dict containing any summary results available after the environment reaches completion (if any).
     - complete: Bool indicating if the environment has reached a completed state and will not iterate further.
    """

    config: DefaultConfig
    param_space: Space
    observation_space: Space
    action_space: Optional[Space]
    history: Dict[str, List[Any]]
    results: Dict[str, Any]
    complete: bool

    @abc.abstractmethod
    def __init__(self, params: Dict[str, Any], config: DefaultConfig):
        """Ready environment for use."""

    def step(
        self, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        """
        Iterate the environment by a single frame/step, if supported by the environment.

        Should return a Tuple matching OpenAI gym interface, i.e. observation, reward, done, info = env.step(action)
          - observation and reward can be none if not relevant to the environment
          - done should always be specified and should indicate if the environment is complete. i.e. If True, subsequent
            step calls are invalid.
          - info can be a flexible dict containing any results or additional info, e.g. a dictionary of results relevant
            to the single step: {'score': 1.01},

        :param action: Optional action to apply to environment (to match OpenAI Gym interface).
        :param kwargs: Flexible kwargs to pass on to environment.
        :return: Tuple containing (observation, reward, done, info) (to match OpenAI Gym interface).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run(
        self, modifiers: Optional[Dict[str, Iterable[Any]]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, List[Any]]]:
        """
        Run the environment to completion.

        For example for an environment that supports stepping/iteration:
        while not self.completed:
            self.step()

        :param modifiers: A dict containing fixed sets of iterables to pass as kwargs to .step(), if supported by env.
                         e.g. a fixed set of actions for 5 steps: {'action': [1, None, 1, 2, 3]}.
        :return: Tuple containing (self.results, self.history).
        """

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the environment to its initial state."""
