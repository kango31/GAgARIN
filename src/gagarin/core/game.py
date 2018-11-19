#!encoding: utf-8
"""
Base class for game engine.
"""

class GameEnded(Exception):
    pass

class Game():
    def __init__(self, logger):
        self._board = None
        self._agents = [ ]
        self._phases = { }
        self._agents_order = None
        self._phases_order = None
        self._board_setup_func = None
        self._logger = logger

    def add_agent(self, agent):
        self._agents.append(agent)

    def clear_agents(self):
        self._agents = [ ]

    def set_agent_oder(self, order):
        self._agents_order = order

    def get_agents(self):
        if self._agents_order is None:
            return self._agents
        else:
            return self._agents_order

    def count_agents(self):
        return len(self._agents)

    def add_phase(self, name, simultaneous=False):
        self._phases[name] = {"simultaneous": simultaneous}

    def clear_phases(self):
        self._phases = { }

    def set_phases_order(self, order):
        self._phases_order = order

    def declare_end(self):
        raise GameEnded

    def mainloop(self):
        #Setup board
        self._game_ended = False
        self._board = self.setup_board()
        #Setup agents
        for agent in self.get_agents():
            agent.reset()
        #Run loop
        while True:
            try:
                #Phases loop
                for phase in self._phases_order:
                    #Setup phase
                    self.prepare_phase(phase)
                    simultaneous = self._phases[phase]["simultaneous"]
                    #Call for actions and resolve
                    if simultaneous:
                        agent_actions = { }
                        for agent in self.get_agents():
                            actions = agent.take_actions(self, phase)
                            agent_actions[agent] = actions
                        for agent in self.get_agents():
                            for action in agent_actions[agent]:
                                self.resolve_action(phase, agent, action)
                    else:
                        for agent in self.get_agents():
                            actions = agent.take_actions(self, phase)
                            for action in actions:
                                self.resolve_action(phase, agent, action)
                    #Terminate phase
                    self.terminate_phase(phase)
            except GameEnded:
                break

    def get_board(self):
        return self._board

    def write_to_log(self, *args, **kwargs):
        """
        Write to log.
        """
        self._logger.write(*args, **kwargs)

    def setup_board(self):
        raise NotImplementedError

    def prepare_phase(self, phase):
        pass

    def terminate_phase(self, phase):
        pass

    def resolve_action(self, phase, agent, action):
        raise NotImplementedError

    def is_legal_action(self, phase, agent, action):
        raise NotImplementedError

    def list_legal_actions(self, phase, agent):
        raise NotImplementedError
