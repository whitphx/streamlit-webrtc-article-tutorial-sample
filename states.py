class StatesObject:
    def __init__(self, is_recording=False, talk_id=None, file_number=0, frame_number=0, is_finished=False):
        self.is_recording = False
        self.talk_id = None
        self.is_finished = False
        self.file_number = 0
        self.frame_number = 0
        self.audios = {}
        
    def __getitem__(self, key):
        if key == "is_recording":
            return self.is_recording
        elif key == "talk_id":
            return self.talk_id
        elif key == "is_finished":
            return self.is_finished
        elif key == "file_number":
            return self.file_number
        elif key == "frame_number":
            return self.frame_number
        elif key == "audios":
            return self.audios
        else:
            raise KeyError(f"{key} is not a valid key")
        
    def get_is_recpording(self):
        return self.is_recording
    
    def get_talk_id(self):
        return self.talk_id
    
    def set_talk_id(self, talk_id):
        self.talk_id = talk_id
        
    def get_is_finished(self):
        return self.is_finished
    
    def set_is_finished(self, is_finished):
        self.is_finished = is_finished
    