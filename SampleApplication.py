import AbstractApplication as Base
from time import sleep

class SampleApplication(Base.AbstractApplication):
    def main(self):
        self.setLanguage('en-US')
        self.sayAnimated('Its lunchtime!')
        sleep(2)

    def onRobotEvent(self, event):
        print(event)


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
