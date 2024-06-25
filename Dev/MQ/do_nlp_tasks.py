NlpTaskDealer = system.import_library('nlp_task_dealer.py').NLPTaskDealer



class Activity:
    def on_start(self):
        self.nlp_dealer = NlpTaskDealer()
        pass

    def on_message(self, channel, message: list):
        if channel == 'deal_nlp_tasks':
            print("*"*20)
            msg = await self.nlp_dealer.deal_nlp_task(*message)
            system.messaging.post('speech_recognized', [msg, "EN"])

    def on_stop(self):
        self.nlp_dealer = None
