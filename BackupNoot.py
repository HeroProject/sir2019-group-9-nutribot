import AbstractApplication as Base
from threading import Semaphore
 
 
class DialogFlowSampleApplication(Base.AbstractApplication):
    def main(self):
        # Set the correct language (and wait for it to be changed)
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()
 
        # Pass the required Dialogflow parameters (add your Dialogflow parameters)
        self.setDialogflowKey('nutribot-igoqwf-ff0373fcda97.json')
        self.setDialogflowAgent('nutribot-igoqwf')

 
        # Make the robot ask the question, and wait until it is done speaking
        self.speechLock = Semaphore(0)
        self.sayAnimated('Hello, what did you eat?')
        self.speechLock.acquire()
 
        # Listen for an answer for at most 9 seconds
        self.meal = None
        self.meals = []
        self.mealLock = Semaphore(0)
        self.setAudioContext('answer_name')
        self.startListening()
        self.mealLock.acquire(timeout=9)
        self.stopListening()
        if not self.meal:  # wait one more second after stopListening (if needed)
            self.mealLock.acquire(timeout=1)
 
        # Respond and wait for that to finish
        if self.meal:
            self.sayAnimated('You had ' + self.meal + '!')
        else:
            self.sayAnimated('Sorry, I didn\'t catch that meal.')
        self.speechLock.acquire()
 
        # Display a gesture (replace <gestureID> with your gestureID)
        self.gestureLock = Semaphore(0)
        self.doGesture('<gestureID>/behavior_1')
        self.gestureLock.acquire()

        return self.meals
 
    def onRobotEvent(self, event):
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
            self.gestureLock.release()
 
    def onAudioIntent(self, *args, intentName):
        if intentName == 'answer_meal' and len(args) > 0:
            self.meal = args[0]
            for arg in args:
                self.meals.append(arg)
            self.mealLock.release()
 
 
# Run the application
sample = DialogFlowSampleApplication()
meals = sample.main()
sample.stop()