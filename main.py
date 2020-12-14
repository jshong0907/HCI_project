from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.utils import *
from random import random
from subprocess import Popen, PIPE

import os

from beautygan import BeautyGAN

img_path = ''
# vertical한 레이아웃
class TempLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(TempLayout, self).__init__(**kwargs)
        self.orientation = "vertical"

# default scrollview
class TempScroll(ScrollView):
    def __init__(self, **kwargs):
        super(TempScroll, self).__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True

class GuideLayout(ScrollView):
    def __init__(self, **kwargs):
        super(GuideLayout, self).__init__(**kwargs)
        self.selectColor = SelectColor()
        self.guide_type = "None"
        self.size=(Window.width, Window.height)
        self.exist=False
        self.selectColor = SelectColor()
        self.guide_type = "None"

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def guide_select(self, paths):
        self.clear_widgets()
        self.add_widget(SelectGuideLayout(paths, size_hint=(1, 1)))


class SelectGuideLayout(GridLayout):
    def __init__(self, paths, **kwargs):
        super(SelectGuideLayout, self).__init__(**kwargs)
        #self.rows=len(paths)
        self.cols=1
        self.spacing=10
        self.size_hint_y=None
        self.bind(minimum_height=self.setter('height'))
        self.first=True
        # self.orientation = 'vertical'
        self.paths = paths
        idx = 0
        for path in self.paths:  
            # guideline = Button(background_normal=path, size_hint_y=None, height=self.width, border=(0, 0, 0, 0))
            guideline = Button(background_normal=path, size_hint=(1, None), size=(self.size[0], 200), border=(0,0,0,0))
            guideline.bind(on_press=self.guideimg_seleted)
            self.add_widget(guideline)
            idx += 1

    def guideimg_seleted(self, instance):
        print(instance.background_normal)
        # pop = PopupLayout(title='guideline', content=Image(source=instance.background_normal), size_hint=(None, None), size=(400, 400))
        # pop.open()

        Popen(['python', 'guide.py', '--path', instance.background_normal], shell=True)
           



class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        #Window.clearcolor = (0.9, 0.9, 0.9, 1)
        self.orientation = "horizontal"
        self.imageLayout = ImageLayout(size_hint=(.6, 1))
        self.interfaceLayout = InterfaceLayout(size_hint=(.4, 1))
        self.padding = [10, 10, 10, 10]
        self.spacing = 10
        self.add_widget(self.imageLayout)
        self.add_widget(self.interfaceLayout)

# LoadDialog
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    

# 시작 시 좌측 이미지 출력
class ImageLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(ImageLayout, self).__init__(**kwargs)
        self.spacing = 10
        self.paintWidget = PaintWidget(size=self.size)
        self.add_widget(self.paintWidget)
        self.btn = Button(background_normal='./images/file_upload.png', size_hint=(.2, .15), pos_hint=({'center_x': 0.5, 'center_y': 0.5}), border=(0, 0, 0, 0))
        self.btn.bind(on_release=self.show_load)
        self.add_widget(self.btn)
        Window.clearcolor = (0.9, 0.9, 0.9, 1)
        with self.canvas.before:
            Color(0.95, 0.95, 0.95)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
            
    def _update_rect(self, instance, value):
        self.rect.pos = self.pos[0], (self.size[1] - self.size[0])/2 + self.pos[0]
        self.rect.size = self.size[0], self.size[0]
    
    loadfile = ObjectProperty(None)

    # LoadDiaglog
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self, instance):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        global img_path
        img_path = filename[0]
        self.rect.source = filename[0]
        self.remove_widget(self.btn)
        self.dismiss_popup()

Factory.register('Root', cls=ImageLayout)
Factory.register('LoadDialog', cls=LoadDialog)

# color를 parameter로 받는 그리기 위젯
class PaintWidget(Widget):
    def __init__(self, color=(0, 0, 0, 0), **kwargs):
        super(PaintWidget, self).__init__(**kwargs)
        self.color = color
        self.brush_size = 2

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*self.color)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.brush_size)
            
    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]

# 그림 우측에 여러 사용자 선택 인터페이스
class InterfaceLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(InterfaceLayout, self).__init__(**kwargs)
        self.orientation = "horizontal"
        
        self.guidelayout = GuideLayout()
        # 좌측에 화장기법 및 브러쉬 선택, 가이드라인 포함 레이아웃
        self.add_widget(MakeupLayout())
        # 우측에 색상 선택 및 가이드라인 선택 레이아웃
        self.add_widget(self.guidelayout)

# 화장기법 및 브러쉬 선택, 가이드라인 포함 레이아웃
class MakeupLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MakeupLayout, self).__init__(**kwargs)
        self.bg = BeautyGAN()
        self.orientation = "vertical"
        # 화장기법 및 브러쉬 선택
        self.add_widget(SelectMakeUp(size_hint=(1, .8)))
        # 가이드라인 선택 버튼
        guideline = Button(background_normal='./images/guideline.png', size_hint=(1, .2), border=(0, 0, 0, 0), size_hint_y=None, height=80)
        guideline.bind(on_press=self.guideline_seleted)
        self.add_widget(guideline)

    def guideline_seleted(self, instance):

        paths = self.bg.run(img_path)
        interface = self.parent
        guidelayout = interface.guidelayout
        
        guidelayout.guide_select(paths)


# 화장기법 및 브러쉬 선택
class SelectMakeUp(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectMakeUp, self).__init__(**kwargs)
        self.orientation = "vertical"
        # 얼굴 부분 선택 ex) 눈, 입술, 얼굴
        self.add_widget(SelectFacePart(part='eye', size_hint=(1, None), height=60))
        self.add_widget(SelectFacePart(part='lip', size_hint=(1, None), height=60))
        self.add_widget(SelectFacePart(part='face', size_hint=(1, None), height=60))
        # 아래 빈 공간을 채워 위로 레이아웃 올리기 위하여
        self.add_widget(TempLayout())

# 얼굴 부분 선택 ex) 눈, 입술, 얼굴
class SelectFacePart(BoxLayout):
    def __init__(self, part='eye', **kwargs):
        super(SelectFacePart, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.btn_pressed=False
        self.tempLayout = TempLayout()
        self.part = part
        self.selectMakeupType = SelectMakeUpType(makeup_type=part)
        self.btn = Button(background_normal="./images/select_"+part+".png", size_hint_y=None, height=60, border=(0,0,0,0))
        self.btn.bind(on_press=self.facepart_selected)
        self.add_widget(self.btn)
        self.add_widget(self.tempLayout)
    
    # 버튼 클릭시 하위 화장기법 선택
    def facepart_selected(self, instance):
        if not self.btn_pressed:
            if self.part == 'lip':
                self.height=180
            else:
                self.height=240
            #self.remove_widget(self.tempLayout)
            self.add_widget(self.selectMakeupType)
            self.btn_pressed = True
        else:
            self.height=60
            self.remove_widget(self.selectMakeupType)
            #self.add_widget(self.tempLayout)
            self.btn_pressed = False


# 화장 기법 선택 ex) 아이웨도우, 마스카라, 아이라이너
class SelectMakeUpType(BoxLayout):
    def __init__(self, makeup_type='eye', **kwargs):
        super(SelectMakeUpType, self).__init__(**kwargs)
        self.orientation="vertical"
        self.size_hint=(1, None)
        self.makeup_types = ["shadow", "mascara", "liner"]
        if makeup_type == 'lip':
            self.makeup_types = ['lipstick', 'tint']
        self.makeup_type_layouts  = []
        for makeup_type in self.makeup_types:
            layout = SelectMakeUpTypeTemp(makeup_type=makeup_type, size_hint_y=None, height=60)
            self.makeup_type_layouts.append(layout)
            self.add_widget(layout)

class SelectMakeUpTypeTemp(BoxLayout):
    def __init__(self, makeup_type="shadow", **kwargs):
        super(SelectMakeUpTypeTemp, self).__init__(**kwargs)
        self.orientation="vertical"
        self.makeup_type=makeup_type
        self.selectBrushType = SelectBrushType(makeup_type=self.makeup_type)
        self.btn_pressed=False
        self.btn = Button(background_normal="./images/select_"+self.makeup_type+".png", size_hint_y=None, height=60, border=(0,0,0,0))
        self.btn.bind(on_press=self.makeuptype_selected)
        self.add_widget(self.btn)
        
    def makeuptype_selected(self, instance):
        selectFacePart = self
        for i in range(2):
            selectFacePart = selectFacePart.parent
        self.selectFacePart = selectFacePart

        if not self.btn_pressed:
            self.selectFacePart.height+=60
            self.size_hint_y=None
            self.height+=60
            self.add_widget(self.selectBrushType)
            self.btn_pressed=True
        else:
            self.selectFacePart.height-=60
            self.height-=60
            self.remove_widget(self.selectBrushType)
            self.btn_pressed=False

            
class SelectBrushType(BoxLayout):
    def __init__(self, makeup_type="liner", **kwargs):
        super(SelectBrushType, self).__init__(**kwargs)
        self.orientation="horizontal"
        self.button_pressed=False
        self.makeup_type = makeup_type
        self.selectColor = SelectColor(makeup_type=self.makeup_type)
        self.spacing=5
        self.button1 = Button(background_normal="./images/brush_1.png", border=(0, 0, 0, 0))
        self.button2 = Button(background_normal="./images/brush_2.png", border=(0, 0, 0, 0))
        self.button3 = Button(background_normal="./images/brush_3.png", border=(0, 0, 0, 0))

        self.button1.bind(on_press=self.brush_selected)
        self.button2.bind(on_press=self.brush_selected)
        self.button3.bind(on_press=self.brush_selected)
        
        self.add_widget(self.button1)
        self.add_widget(self.button2)
        self.add_widget(self.button3)

    def brush_selected(self, instance):
        main_layout = self
        for i in range(7):
            main_layout = main_layout.parent
        self.main_layout = main_layout
        if instance == self.button1:
            self.paintWidget = self.main_layout.imageLayout.paintWidget.brush_size=1
        if instance == self.button2:
            self.paintWidget = self.main_layout.imageLayout.paintWidget.brush_size=2
        if instance == self.button3:
            self.paintWidget = self.main_layout.imageLayout.paintWidget.brush_size=3
        self.guidelayout = self.main_layout.interfaceLayout.guidelayout
        self.guidelayout.clear_widgets()
        self.guidelayout.selectColor.change_color(makeup_type=self.makeup_type)
        self.guidelayout.add_widget(self.guidelayout.selectColor)
        self.guidelayout.guide_type = 'color'
           
        

class SelectColor(GridLayout):
    def __init__(self, makeup_type='liner', **kwargs):
        super(SelectColor, self).__init__(**kwargs)
        self.cols=2
        self.color_buttons = []
        colors = ['ross-kiss', 'red', 'green']

        for color in colors:
            btn = Button(text=color)
            btn.bind(on_press=self.color_selected)
            self.add_widget(btn)
            self.color_buttons.append(btn)
    
    def change_color(self, makeup_type='liner'):
        self.clear_widgets()
        self.color_buttons.clear()
        if makeup_type=='shadow':
            color_list=['golden\nbrown', 'mat\nsand', 'mypitch', 'deep\nnight', 'milkyway', 'Rose\nmacaron', 'Sweet\nrose', 'Vine', 'Sparkling\npink', 'Pink\nmoscato', 'Champagne\nparty']
        elif makeup_type=='mascara':
            color_list=['black', 'rosy\nbrown', 'brown', 'natural', 'Gray', 'Clear\nblack', 'Innocent\nbrown', 'Mystical\nPlum\nBurgundy']
        elif makeup_type=='liner':
            color_list=['liner1', 'liner2', 'liner3']
        for color in color_list:
            real_color = get_random_color(0.6)
            if color=="golden\nbrown":
                real_color=(0.819, 0.55, 0.45, 0.6)
            elif color=="mat\nsand":
                real_color=(0.9, 0.74, 0.66, 0.6)
            elif color=="mypitch":
                real_color=(0.96, 0.78, 0.69, 0.6)
            elif color=="deep\nnight":
                real_color=(0.66, 0.43, 0.38, 0.6)
            elif color=="milkyway":
                real_color=(0.83, 0.78, 0.74, 0.6)
            elif color=="black":
                real_color=(0.7, 0.7, 0.7, 0.6)
            elif color=="rosy\nbrown":
                real_color=(0.65, 0.31, 0.33, 0.6)
            elif color=="brown":
                real_color=(0.96, 0.78, 0.69, 0.6)
            elif color=="liner1":
                real_color=(0.19,0.19,0.24,0.6)
            elif color=="liner2":
                real_color=(0.34,0.27,0.27,0.6)
            elif color=="liner3":
                real_color=(0.41,0.27,0.27,0.6)
            btn = Button(text=color, font_size=10, halign='center', background_color=real_color, size_hint_y=None, height=90)
            btn.bind(on_press=self.color_selected)
            self.add_widget(btn)
            self.color_buttons.append(btn)

    def color_selected(self, instance):
        main_layout = self
        for i in range(3):
            main_layout = main_layout.parent
        self.main_layout = main_layout
        self.paintWidget = self.main_layout.imageLayout.paintWidget
        color = (random(), random(), random(), 0.6)
        if instance.text=="golden\nbrown":
            color=(0.819, 0.55, 0.45, 0.6)
        elif instance.text=="mat\nsand":
            color=(0.9, 0.74, 0.66, 0.6)
        elif instance.text=="mypitch":
            color=(0.96, 0.78, 0.69, 0.6)
        elif instance.text=="deep\nnight":
            color=(0.66, 0.43, 0.38, 0.6)
        elif instance.text=="milkyway":
            color=(0.83, 0.78, 0.74, 0.6)
        elif instance.text=="black":
            color=(0.7, 0.7, 0.7, 0.6)
        elif instance.text=="rosy\nbrown":
            color=(0.65, 0.31, 0.33, 0.6)
        elif instance.text=="brown":
            color=(0.96, 0.78, 0.69, 0.6)
        self.paintWidget.color=color
                

# 스크롤 뷰로 생성
'''
class SelectMakeUpType(ScrollView):
    def __init__(self, makeup_types=["shadow", "mascara", "eyeliner"], **kwargs):
        super(SelectMakeUpType, self).__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.size_hint=(1, None)
        self.makeup_type_buttons = []
        self.main_layout = TempLayout(size_hint_y=None)
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))
        for makeup_type in makeup_types:
            btn = Button(text=makeup_type, size_hint_y=None, height=60)
            self.makeup_type_buttons.append(btn)
            self.main_layout.add_widget(btn)
        self.add_widget(self.main_layout)
'''

class GuideLineApp(App):
    def build(self):
        Window.size = (1200, 720)
        return MainLayout()


if __name__ == '__main__':
    GuideLineApp().run()