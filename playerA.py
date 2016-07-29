# coding=utf-8
# !/usr/bin/env python
import json
from random import randint

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour


class PlayerAAgent(Agent):
    class Play(Behaviour):

        msg = None
        initial_guess = randint(0, 1000)
        low_state = 0
        high_state = 1000

        def _process(self):
            self.msg = self._receive(True)

            if self.msg:
                request = json.loads(self.msg.content)
                if request['request_type'] == 'play':
                    initial_guess = randint(self.low_state, self.high_state)
                    ask_help = {'request_type': 'help_request', 'number': initial_guess, 'origin': 'gamer3@127.0.0.1'}
                    self.send_message(ask_help, 'coordinator@127.0.0.1')

                if request['request_type'] == 'help_response':
                    if request['status'] == "high":
                        self.high_state = self.initial_guess
                        new_guess = randint(self.low_state, self.high_state)
                        travel = {'request_type': 'guess', 'origin': 'gamer3@127.0.0.1', 'number': new_guess}
                        self.send_message(travel, 'coordinator@127.0.0.1')

                    if request['status'] == "low":
                        self.low_state = self.initial_guess
                        new_guess = randint(self.low_state, self.high_state)
                        travel = {'request_type': 'guess', 'origin': 'gamer3@127.0.0.1', 'number': new_guess}
                        self.send_message(travel, 'coordinator@127.0.0.1')

                    if request['status'] == "ok":
                        travel = {'request_type': 'guess', 'origin': 'gamer3@127.0.0.1', 'number': self.initial_guess}
                        self.send_message(travel, 'coordinator@127.0.0.1')

                if request['request_type'] == 'round_result':
                    if request['result'] == "win":
                        print "YAAAAY! I won!"

                    if request['result'] == "late":
                        print ":(((((((((((((((("

                    if request['result'] == "no":
                        initial_guess = randint(self.low_state, self.high_state)
                        ask_help = {'request_type': 'help_request', 'number': initial_guess,
                                    'origin': 'gamer3@127.0.0.1'}
                        self.send_message(ask_help, 'coordinator@127.0.0.1')

        def say_ready(self):
            travel = {'request_type': 'player_ready', 'origin': 'gamer3@127.0.0.1'}
            self.send_message(travel, 'coordinator@127.0.0.1')

        def send_message(self, content, address):

            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("game")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(json.dumps(content))
            self.myAgent.send(self.msg)
            print '\nMessage %s sent to %s' % (content, address)

    def _setup(self):
        print "\n Agent\t" + self.getAID().getName() + " is up"

        game_template = ACLTemplate()
        game_template.setOntology('game')

        message_template = MessageTemplate(game_template)
        settings = self.Play()
        self.addBehaviour(settings, message_template)
        settings.say_ready()


if __name__ == '__main__':
    PlayerAAgent('gamer3@127.0.0.1', 'game1').start()
