from dataclasses import dataclass
import data

@dataclass
class Image:
    ImageId: str = None
    ImageFileName: str = None
    FileName: str = None
    FileType: str = None
    StatusType: str = None
    ContentType: str = None

    def __post_init__(self):
        if not self.ImageId and not self.ImageFileName:
            return

        df = data.v_Image()

        if self.ImageId:
            df = df[df['ImageId'] == str(self.ImageId).upper()]
        else:
            df = df[df['ImageFileName'] == self.ImageFileName]

        if not df.empty:
            row = df.iloc[0]
            self.ImageId = self.ImageId or row['ImageId']
            self.FileName = self.FileName or row['FileName']
            self.FileType = self.FileType or row['FileType']
            self.StatusType = self.StatusType or row['StatusType']
            self.ContentType = self.ContentType or row['ContentType']
            self.ImageFileName = self.ImageFileName or row['ImageFileName']
        else:
            self.ImageId = None
            self.ImageFileName = None
