'''各モジュール間共通のものを格納します'''

class Share:
    __title = None
    @classmethod
    @property
    def version(cls):
        return 0.1
    @classmethod
    @property
    def maincolor(cls):
        return '#7062af'
    @classmethod
    @property
    def topBarHeight(cls):
        return 50
    @property
    def title(cls):
        '''現在作成中の劇の名前'''
        return Share.__title
    @title.setter
    def title(self, newTitle):
        Share.__title = newTitle
