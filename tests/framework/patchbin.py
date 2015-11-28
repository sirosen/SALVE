class PatchBin(object):
    def __init__(self):
        self.patches = set()

    def setUp(self):
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
