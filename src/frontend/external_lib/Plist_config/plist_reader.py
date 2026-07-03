import xml.sax
from external_lib.Plist_config import PListReader


# class Plist_reader(object):
class Plist_reader:
    def read(self, sFile_content):
        # parse the file
        reader = PListReader.PListReader()
        xml.sax.parseString(sFile_content, reader, reader.getRecommendedFeatures())
        dConfig = reader.getResult()
        return dConfig
