# coding=utf-8
# !/usr/bin/env python
import json

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour


class PlayerAgent(Agent):
    class Play(Behaviour):

        msg = None

        def _process(self):
            self.msg = self._receive(True)

            if self.msg:
                request = json.loads(self.msg.content)
                if request['request_type'] == 'offer_response':
                    print 'prvi'

                if request['request_type'] == 'discount_response':
                    print 'drugi'

        def say_ready(self):
            travel = {'request_type': 'player_ready', 'origin': 'playerB@127.0.0.1'}
            self.send_message(json.dumps(travel), 'coordinator@127.0.0.1')

        def send_message(self, content, address):

            agent = spade.AID.aid(name=address, addresses=["xmpp://%s"])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("game")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)
            self.myAgent.send(self.msg)
            print '\nMessage %s sent to %s' % (content, address)

    def _setup(self):
        print "\n Agent\t" + self.getAID().getName() + " is up"

        feedback_template = ACLTemplate()
        feedback_template.setOntology('game')

        message_template = MessageTemplate(feedback_template)
        settings = self.Play()
        self.addBehaviour(settings, message_template)
        settings.say_ready()


if __name__ == '__main__':
    PlayerAgent('playerB@127.0.0.1', 'game').start()
