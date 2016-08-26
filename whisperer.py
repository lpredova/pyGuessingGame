# coding=utf-8
# !/usr/bin/env python
import json

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import BDIAgent
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour
from spade.DF import Service
from spade.bdi import Goal, expr


class Whisperer(BDIAgent):
    class Evaluate(Service):
        inputs = {}
        outputs = {}

        def run(self):
            self.MyAgent.addBelieve(expr("Vrijednost(gamer2)"))

    class Whisper(Behaviour):

        msg = None
        selected_number = 0

        def _process(self):
            self.msg = self._receive(True)

            if self.msg:
                request = json.loads(self.msg.content)
                if request['request_type'] == 'new_number':
                    self.selected_number = request['number']
                    print "I got it..."

                if request['request_type'] == 'help_request':

                    number = request['number']
                    response = ""

                    if self.myAgent.askBelieve(expr('Vrijednost(gamer2)')):

                        if request['origin'] == "gamer2@127.0.0.1":

                            if self.selected_number < int(number):
                                response = "high"
                            if self.selected_number > int(number):
                                response = "low"
                            if self.selected_number == int(number):
                                response = "ok"

                        else:
                            response = "ok"

                    player_help = {'request_type': 'help_response', 'status': response}
                    self.send_message(player_help, request['origin'])
                    print 'I told %s that %i is %s' % (request['origin'], number, response)

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

        self.addBelieve(expr('Vrijednost(gamer2)'))

        s1 = self.Evaluate(P=expr("Vrijednost( 0 )"), Q=expr("Vrijednost( 1 )"))
        # self.addPlan(self.bdiBehav, None, P=expr('Sadrzim( 1, 0 )'), Q=expr('Sadrzim( 2, 0 )'))

        g = Goal(expr('Pobjeda(gamer2)'))
        self.addGoal(g)

        settings = self.Whisper()
        self.addBehaviour(settings, message_template)


if __name__ == '__main__':
    Whisperer('whisperer@127.0.0.1', 'game').start()
