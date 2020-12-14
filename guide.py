import os
os.environ['KIVY_NO_ARGS'] = '1'

import argparse
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle



class GuideLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(GuideLayout, self).__init__(**kwargs)
        #self.path = path

        with self.canvas.before:
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
            self.rect.source = img_path

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


        # self.rec = Rectangle(size=self.size, pos=self.pos)
        # self.rec.source = 'imgs/no_makeup/test.png'



class GuideScreen(App):

    def build(self):
        return GuideLayout()





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='imgs/no_makeup/test.png')
    args = parser.parse_args()

    global img_path
    img_path = args.path
    print(img_path)
    GuideScreen().run()