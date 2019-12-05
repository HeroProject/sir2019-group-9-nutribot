import AbstractApplication as Base
from threading import Semaphore


class NutribotApplication(Base.AbstractApplication):
    def main(self):
        # Set the correct language (and wait for it to be changed)
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Pass the required Dialogflow parameters (add your Dialogflow parameters)
        self.setDialogflowKey('nutribot-igoqwf-ef32d473df4d.json')
        self.setDialogflowAgent('nutribot-igoqwf')

        # Make the robot ask the question, and wait until it is done speaking
        self.speechLock = Semaphore(0)
        self.sayAnimated('Hi, I\'m Noot! What is your name?')
        self.speechLock.acquire()

        # Listen for an answer for at most 5 seconds
        self.name = None
        self.nameLock = Semaphore(0)
        self.setAudioContext('answer_name')
        self.startListening()
        self.nameLock.acquire(timeout=5)
        self.stopListening()
        if not self.name:  # wait one more second after stopListening (if needed)
            self.nameLock.acquire(timeout=1)

        # Respond and wait for that to finish
        if self.name:
            self.sayAnimated('Nice to meet you ' + self.name + '!')
        else:
            self.sayAnimated('Sorry, I didn\'t catch your name.')
        self.speechLock.acquire()

        # Display a gesture (replace <gestureID> with your gestureID)
        # self.gestureLock = Semaphore(0)
        # self.doGesture('<gestureID>/behavior_1')
        # self.gestureLock.acquire()

        # Testing module
        self.speechLock = Semaphore(0)
        self.sayAnimated('Oh, why haven\'t you eaten yet?')
        self.speechLock.acquire()

        self.negativeFlow()

        quit('done')

        # Main interaction loop
        done = False
        while done is False:
            print("ey")
            # Inquire about meal
            self.speechLock = Semaphore(0)
            self.sayAnimated('So, what did you eat?')
            self.speechLock.acquire()

            # register a meal event
            self.mealEvent()

            if self.flow == 'suggestion':
                self.suggestionFlow()

            elif self.flow == 'negative':

                self.sayAnimated('Oh, why haven\'t you eaten yet?')
                self.negativeFlow()
                self.speechLock.acquire()

            elif self.flow == 'failure':
                self.sayAnimated('Sorry, I couldn\'t register your meal.')
                self.speechLock.acquire()


    def onRobotEvent(self, event):
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
            self.gestureLock.release()

    def onAudioIntent(self, *args, intentName):
        if intentName == 'answer_name' and len(args) > 0:
            self.name = args[0]
            self.nameLock.release()
        elif intentName == 'input_meal' and len(args) > 0:
            self.meal = args[0]
            self.mealLock.release()
        elif intentName == 'no_meal' and len(args) > 0:
            print("neg no meal", args)
            self.negativeReason = args[0]
            self.negativeReasonLock.release()

    def mealEvent(self):
        self.meal = None
        self.flow = None
        self.mealLock = Semaphore(0)
        self.setAudioContext('input_meal')
        self.startListening()
        self.mealLock.acquire(timeout=5)
        self.stopListening()
        if not self.meal:  # wait one more second after stopListening (if needed)
            self.mealLock.acquire(timeout=1)

        if self.meal == 'No':
            self.flow = 'negative'

        elif self.meal:
            self.sayAnimated("Okay, great! I\'ve registered everything.")
            self.speechLock.acquire()
            self.flow = 'suggestion'

        else:
            self.flow = 'failure'

    def suggestionFlow(self):
        self.speechLock = Semaphore(0)
        self.sayAnimated('Can I give you a dietary suggestion?')
        self.speechLock.acquire()

        self.wantsSuggestion = None
        self.wantsSuggestionLock = Semaphore(0)
        self.setAudioContext('yesno')
        self.startListening()
        self.wantsSuggestionLock.acquire(timeout=5)
        self.stopListening()
        if not self.wantsSuggestion:  # wait one more second after stopListening (if needed)
            self.wantsSuggestionLock.acquire(timeout=1)

        if not self.wantsSuggestion:
            self.sayAnimated('Sorry, I didn\'t catch that.')
            self.speechLock.acquire()
        elif self.wantsSuggestion =='yes':
            self.sayAnimated('You might want to eat more fiber and make sure you stay away from sugar. Also, make sure you drink plenty of water. It is recommended to drink 2 liters per day. ')
            self.speechLock.acquire()
        elif self.wantsSuggestion == 'no':
            self.sayAnimated('Go fuck yourself then.')
            self.speechLock.acquire()

    def negativeFlow(self):
        print("in negativeflow")
        self.negativeReason = None
        self.negativeReasonLock = Semaphore(0)
        self.setAudioContext('no_meal')
        self.startListening()
        self.negativeReasonLock.acquire(timeout=5)
        self.stopListening()

        print(self.negativeReason)

        if not self.negativeReason:  # wait one more second after stopListening (if needed)
            self.negativeReasonLock.acquire(timeout=1)
            print("if not")
        if self.negativeReason == 'Forgot':
            self.speechLock = Semaphore(0)
            self.sayAnimated('It\'s past meal time! Time to eat.')
            self.speechLock.acquire()
            print(self.negativeReason)
        elif self.negativeReason == 'Time':
            self.speechLock = Semaphore(0)
            self.sayAnimated('That\'s too bad! I\'ll ask you again in an hour.')
            self.speechLock.acquire()

# Run the application
nutribot = NutribotApplication()
nutribot.main()
nutribot.stop()