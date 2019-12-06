import AbstractApplication as Base
from threading import Semaphore
from statistics import mean, stdev

class NutribotApplication(Base.AbstractApplication):
    def main(self):
        # Set the correct language (and wait for it to be changed)
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Pass the required Dialogflow parameters (add your Dialogflow parameters)
        self.setDialogflowKey('nutribot-igoqwf-29c25ede3da3.json')
        self.setDialogflowAgent('nutribot-igoqwf')

        # Make the robot ask the question, and wait until it is done speaking
        self.speechLock = Semaphore(0)
        self.sayAnimated('Hi, I\'m Noot! What is your name?')
        self.speechLock.acquire()

        self.meal_history = {"carbs": 0, "fruits": 0, "vegetables": 0, "dairy": 0, "protein": 0, "sugar": 0}

        self.healthy_meals = ["fruits", "vegetables", "protein"]
        self.unhealthy_meals = ["carbs", "dairy", "sugar"]

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
            print(self.name)
        else:
            self.sayAnimated('Sorry, I didn\'t catch your name.')
        self.speechLock.acquire()

        # Display a gesture (replace <gestureID> with your gestureID)
        # self.gestureLock = Semaphore(0)
        # self.doGesture('<gestureID>/behavior_1')
        # self.gestureLock.acquire()

        # Testing module
        # self.speechLock = Semaphore(0)
        # self.sayAnimated('Oh, why haven\'t you eaten yet?')
        # self.speechLock.acquire()
        #
        # self.negativeFlow()

        # quit('done')

        # Main interaction loop
        done = False
        while done is False:
            print("LOOP\n")
            print(self.meal_history)
            # Inquire about meal
            self.speechLock = Semaphore(0)
            self.sayAnimated('So, what did you eat?')
            self.speechLock.acquire()

            # register a meal event
            self.mealEvent()

            if self.flow == 'suggestion':
                self.suggestionFlow()
                self.speechLock.acquire()

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
            # for arg in args:
                # self.meals.append(arg)
            print(args)
            self.meal = args[0]
            self.mealLock.release()
        elif intentName == 'no_meal' and len(args) > 0:
            print("neg no meal", args)
            self.negativeReason = args[0]
            self.negativeReasonLock.release()
        elif intentName == "yesno" and len(args)>0:            
            self.wantsSuggestion = args[0]

    def mealEvent(self):
        self.meal = None
        self.flow = None
        self.mealLock = Semaphore(0)
        self.setAudioContext('input_meal')
        self.startListening()
        self.mealLock.acquire(timeout=5)
        self.stopListening()
        print(self.meal)


        if not self.meal:  # wait one more second after stopListening (if needed)
            self.mealLock.acquire(timeout=1)

        # if self.meal == 'No':
        #     self.flow = 'negative'

        elif len(self.meal) > 0:
            print(self.meal)
            self.meal_history[self.meal] += 1
            self.sayAnimated("Okay, great! I\'ve registered "+str(self.meal))
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

        print(self.wantsSuggestion)
        if not self.wantsSuggestion:
            self.sayAnimated('Sorry, I didn\'t catch that.')
            self.speechLock.acquire()

        elif self.wantsSuggestion == 'yes':
            max_group = max(self.meal_history.keys(), key=(lambda key: self.meal_history[key]))
            min_group = min(self.meal_history.keys(), key=(lambda key: self.meal_history[key]))
            meal_avg = mean(self.meal_history.values())
            meal_std = stdev(self.heal_history.values())

            uneaten = []
            for k,v in self.meal_history.items():
                if v == self.meal_history[min_group] and v == 0:
                    uneaten.append(k)

            if meal_avg > 1:
                if meal_std > meal_avg:
                    print("Your diet could use some more balance.")
                else:
                    print("Your diet is balanced, good job!")

            if max_group in self.unhealthy_meals:
                self.sayAnimated("Woah, you've had a lot of " + max_group + " today. You might want to eat more fiber and stay away from sugar. And don't forget to hydrate!")
                self.speechLock.acquire()
            elif max_group in self.healthy_meals:
                print("Good job! " + max_group + " are healthy for you.")
                if max_group == "vegetables":
                    print("Plenty of greens! Reward yourself with a snack!")


            # if user is lactose intolerant and self.meal_history["dairy"] > 0:
            # "Careful with your dairy intake"



        elif self.wantsSuggestion == 'no':
            self.sayAnimated('Okay, that is fine for now, but please let me know if you would like some advice and I would be happy to help!')
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