# coding=utf-8
# !/usr/bin/env python
import json
from random import randint

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour


class GameCoordinator(Agent):
    class Coordinate(Behaviour):

        msg = None
        ready = 0
        selected_number = 0
        requests = []
        won = False

        def _process(self):
            self.msg = self._receive(True)

            if self.msg:
                request = json.loads(self.msg.content)
                if request['request_type'] == 'player_ready':

                    self.ready += 1
                    self.requests.append(request['origin'])

                    if self.ready == 2:
                        self.selected_number = randint(0, 1000)
                        inform_whisperer = {'request_type': 'new_number', 'number': self.selected_number}
                        self.send_message(inform_whisperer, 'whisperer@127.0.0.1')

                        for origin in self.requests:
                            inform_player = {'request_type': 'play'}
                            self.send_message(inform_player, origin)

                if request['request_type'] == 'guess':

                    if self.won:
                        inform_whisperer = {'request_type': 'round_result', 'result': 'late'}
                        self.send_message(inform_whisperer, request['origin'])

                    if request['number'] == self.selected_number:
                        self.won = True
                        inform_whisperer = {'request_type': 'round_result', 'result': 'win'}
                        self.send_message(inform_whisperer, request['origin'])
                    else:
                        inform_whisperer = {'request_type': 'round_result', 'result': 'no'}
                        self.send_message(inform_whisperer, request['origin'])

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

        feedback_template = ACLTemplate()
        feedback_template.setOntology('game')

        message_template = MessageTemplate(feedback_template)
        settings = self.Coordinate()
        self.addBehaviour(settings, message_template)


if __name__ == '__main__':
    GameCoordinator('coordinator@127.0.0.1', 'game').start()
