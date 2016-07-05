########################################
# Filename: LoadUtility.py
# Created by: blach (18Apr15)
########################################

class LoadUtility:

    def __init__(self, callback):
        self.callback = callback
        self.models = []

    def load(self):
        for modelFile in self.models:
            loader.loadModel(modelFile)
            loader.progressScreen.tick()
        self.done()

    def done(self):
        self.callback()
        self.destroy()

    def destroy(self):
        self.models = None
        self.callback = None
