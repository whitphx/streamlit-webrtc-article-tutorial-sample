class StatesObject:
    def __init__(self, is_recpording=False, talk_id=None, file_number=0, frame_number=0, is_finished=False):
        self.is_recpording = False
        self.talk_id = None
        self.is_finished = False
        self.file_number = 0
        self.frame_number = 0
        self.audios = {}
        
    def get_is_recpording(self):
        return self.is_recpording
    
    def get_talk_id(self):
        return self.talk_id
    
    def set_talk_id(self, talk_id):
        self.talk_id = talk_id
        
    def get_is_finished(self):
        return self.is_finished
    
    def set_is_finished(self, is_finished):
        self.is_finished = is_finished
    