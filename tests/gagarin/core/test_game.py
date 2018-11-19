#!encoding: utf-8

import pytest

from gagarin.core.board import Board
from gagarin.core.zone import Zone
from gagarin.core.deck import Deck
from gagarin.core.card import Card
from gagarin.core.agent import Agent
from gagarin.core.game import Game


@pytest.fixture(scope="module")
def standard_deck():
    deck = Deck(name="Deck")
    facevalues=["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
    colours = [u"\u2660", u"\u2665", u"\u2666", u"\u2663"] #Spades, Hearts, Diamonds, Clubs
    class MyCard(Card):
        def __init__(self, facevalue, colour):
            Card.__init__(self, facevalue=facevalue, colour=colour)
            try:
                self._score = int(facevalue)
            except ValueError:
                self._score = {"J": 11, "Q": 12, "K": 13, "A": 14}[facevalue]
        def __str__(self):
            return u"{}{}".format(self.facevalue, self.colour)
        def __gt__(self, other):
            return self._score > other._score
        def __lt__(self, other):
            return self._score < other._score
        def __eq__(self, other):
            return self._score == other._score

    for c in colours:
        for fv in facevalues:
            deck.add(MyCard(facevalue=fv, colour=c))
    deck.shuffle()
    yield deck


@pytest.fixture(scope="module")
def battle(standard_deck):
    class Battle(Game):
        def __init__(self, max_turns, *args, **kwargs):
            super(Battle, self).__init__(*args, **kwargs)
            self.add_phase("main", simultaneous=True)
            self.set_phases_order(["main"])
            self._components = { }
            self._max_turns = max_turns

        def setup_board(self):
            #Initialisation
            self.write_to_log("Setting up the board...\n")
            board = Board(name="Board", turn=0)
            self.write_to_log("   board: {}\n".format(board.name))
            #Draw cards
            nb_cards = len(standard_deck) / self.count_agents()
            piles = standard_deck.deal(self.count_agents(), nb_cards)
            #Create player area
            for agent, pile in zip(self.get_agents(), piles):
                self._components[agent] = { }
                zone = Zone(name=agent.get_name())
                board.add(zone)
                deck = Deck(name="{}/Deck".format(agent.get_name()))
                self.write_to_log("   setup deck: {}\n".format(deck.name))
                for card in pile:
                    deck.add(card)
                zone.add(deck)
                self._components[agent]["deck"] = deck
                discard = Deck(name="{}/Discard".format(agent.get_name()),
                        face_up=True)
                self.write_to_log("   setup discard: {}\n".format(discard.name))
                zone.add(discard)
                self._components[agent]["discard"] = discard
                area = Zone(name="{}/PlayArea".format(agent.get_name()))
                zone.add(area)
                self._components[agent]["area"] = area
                self.write_to_log("   setup play area: {}\n".format(area.name))
            self.write_to_log("Board setup complete!\n")
            return board

        def prepare_phase(self, phase):
            board = self.get_board()
            if phase == "main":
                if board.turn == 0:
                    self.write_to_log("New game of Battle !\n")
                board.turn += 1
                self.write_to_log("Turn: {}\n".format(board.turn))
                #Reshuffle deck ?
                for agent in self.get_agents():
                    deck_name = "{}/Deck".format(agent.get_name())
                    deck = self.get_board().search_component("name == '{}'"
                            .format(deck_name))
                    discard_name = "{}/Discard".format(agent.get_name())
                    discard = self.get_board().search_component("name == '{}'"
                            .format(discard_name))
                    if deck.is_empty():
                        cards = discard.draw_all()
                        for card in cards:
                            deck.add(card)
                        deck.shuffle()
                        self.write_to_log("   {} deck is empty, reshuffle "
                                "discard. He/she now has {} cards\n"
                                .format(agent.get_name(), len(deck)))
                        if deck.is_empty():
                            self.write_to_log("   {} has lost the game\n"
                                    .format(agent.get_name()))
                            self.write_to_log("Game now ends.\n")
                            self.declare_end()

        def terminate_phase(self, phase):
            board = self.get_board()
            if phase == "main":
                #Get cards in the play area
                top_cards = [ ]
                agents = [ ]
                areas = [ ]
                discards = [ ]
                for agent in self.get_agents():
                    area = self._components[agent]["area"]
                    discard = self._components[agent]["discard"]
                    for card in area:
                        pass
                    top_cards.append(card)
                    agents.append(agent)
                    areas.append(area)
                    discards.append(discard)
                    #self.write_to_log("   {} last card is: {}\n".format(
                    #        agent.get_name(), card))
                #Check who has won
                winner = None
                if top_cards[0].is_face_down() and top_cards[1].is_face_down():
                    return
                if top_cards[0] > top_cards[1]:
                    self.write_to_log("   {} wins\n".format(
                            agents[0].get_name()))
                    winner = 0
                elif top_cards[0] < top_cards[1]:
                    self.write_to_log("   {} wins\n".format(
                            agents[1].get_name()))
                    winner = 1
                else:
                    self.write_to_log("   Battle !\n")
                if winner is not None:
                    loot = [ ]
                    for area in areas:
                        local_loot = [ ]
                        for card in area:
                            local_loot.append(card)
                        for card in local_loot:
                            area.remove(card)
                        loot.extend(local_loot)
                    for card in loot:
                        discards[winner].add(card)
                    self.write_to_log("   {} now has {} cards in his/her "
                            "discard\n".format(agents[winner].get_name(),
                            len(discards[winner])))
                    self.write_to_log("      ")
                    for card in discards[winner]:
                        self.write_to_log("{} ".format(card))
                    self.write_to_log("\n")

                if board.turn >= self._max_turns:
                    self.write_to_log("Game now ends.\n")
                    self.declare_end()

        def is_legal_action(self, phase, agent, action):
            #Get agent play area
            play_area_name = "{}/PlayArea".format(agent.get_name())
            play_area = self.get_board().search_component(
                    "name == '{}'".format(play_area_name))
            if play_area.is_empty():
                #If it's empty you can only play a card face up
                if action == ('Play', 'face up'):
                    return True
                else:
                    return False
            else:
                #If it's not empty, it's a battle
                last_is_visible = False
                for card in play_area:
                    last_is_visible = card.is_face_up()
                    #self.write_to_log("   card: {}\n".format(card))
                #self.write_to_log("   last card visible: {}\n".format(last_is_visible))
                if action == ('Play', 'face down'):
                    return last_is_visible
                else:
                    return not last_is_visible

        def list_legal_actions(self, phase, agent):
            all_actions = [('Play', 'face up'), ('Play', 'face down')]
            return list(filter(lambda x: self.is_legal_action(phase, agent, x),
                    all_actions))

        def resolve_action(self, phase, agent, action):
            if phase == "main":
                deck_name = "{}/Deck".format(agent.get_name())
                deck = self.get_board().search_component("name == '{}'".format(
                        deck_name))
                play_area_name = "{}/PlayArea".format(agent.get_name())
                play_area = self.get_board().search_component(
                        "name == '{}'".format(play_area_name))
                if action == ('Play', 'face up'):
                    card = deck.draw(face_up=True)[0]
                    self.write_to_log("   {} plays {}\n".format(agent.get_name(),
                            card))
                    play_area.add(card)
                elif action == ('Play', 'face down'):
                    card = deck.draw(face_up=False)[0]
                    play_area.add(card)
                    self.write_to_log("   {} plays a card face down\n".format(
                            agent.get_name()))
                    #self.write_to_log("   visible: {}\n".format(
                    #        card.is_face_up()))

    with open("/tmp/Battle.log", "w") as logger:
        yield Battle(1000, logger)


class MyAgent(Agent):
    def take_actions(self, game, phase):
        #Get all posible actions
        all_actions = game.list_legal_actions(phase, self)
        #Pick one
        if len(all_actions) > 0:
            return [all_actions[0]]
        else:
            return [ ]


class TestGame(object):
    def test_get(self, battle):
        player1 = MyAgent(name="Cédric")
        player2 = MyAgent(name="IA")
        battle.add_agent(player1)
        battle.add_agent(player2)
        battle.mainloop()
        assert battle.get_board().get("name") == "Board"
