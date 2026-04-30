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
            self.ImageId = row['ImageId']
            self.FileName = row['FileName']
            self.FileType = row['FileType']
            self.StatusType = row['StatusType']
            self.ContentType = row['ContentType']
            self.ImageFileName = row['ImageFileName']
        else:
            self.ImageId = None
            self.ImageFileName = None
