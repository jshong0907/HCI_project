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
from kivy.core.image import Image
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup


import os

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

class GuideLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(GuideLayout, self).__init__(**kwargs)
        self.selectColor = SelectColor()
        self.guide_type = "None"

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
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
class ImageLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ImageLayout, self).__init__(**kwargs)
        self.spacing = 10
        self.paintWidget = PaintWidget(size=self.size)
        self.add_widget(self.paintWidget)
        self.btn = Button(text='File Load', size_hint=(None, .1), pos_hint=({'center_x': 0.5, 'center_y': 0.5}))
        self.btn.bind(on_release=self.show_load)
        self.add_widget(self.btn)

        with self.canvas.before:
            self.rect = Rectangle(source = "./test.jpg", size=self.size, pos=self.pos)
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
        print(self.size)
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
        self.spacing = 10
        self.guidelayout = GuideLayout()
        # 좌측에 화장기법 및 브러쉬 선택, 가이드라인 포함 레이아웃
        self.add_widget(MakeupLayout())
        # 우측에 색상 선택 및 가이드라인 선택 레이아웃
        self.add_widget(self.guidelayout)

# 화장기법 및 브러쉬 선택, 가이드라인 포함 레이아웃
class MakeupLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MakeupLayout, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        # 화장기법 및 브러쉬 선택
        self.add_widget(SelectMakeUp(size_hint=(1, .8)))
        # 가이드라인 선택 버튼
        self.add_widget(Button(text='Guideline', size_hint=(1, .2)))

# 화장기법 및 브러쉬 선택
class SelectMakeUp(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectMakeUp, self).__init__(**kwargs)
        self.orientation = "vertical"
        # 얼굴 부분 선택 ex) 눈, 입술, 얼굴
        self.add_widget(SelectFacePart(part='EYE', size_hint=(1, None), height=60))
        self.add_widget(SelectFacePart(part='LIP', size_hint=(1, None), height=60))
        self.add_widget(SelectFacePart(part='FACE', size_hint=(1, None), height=60))
        # 아래 빈 공간을 채워 위로 레이아웃 올리기 위하여
        self.add_widget(TempLayout())

# 얼굴 부분 선택 ex) 눈, 입술, 얼굴
class SelectFacePart(BoxLayout):
    def __init__(self, part='EYE', **kwargs):
        super(SelectFacePart, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.btn_pressed=False
        self.tempLayout = TempLayout()
        self.selectMakeupType = SelectMakeUpType()
        self.btn = Button(text=part, size_hint_y=None, height=60)
        self.btn.bind(on_press=self.facepart_selected)
        self.add_widget(self.btn)
        self.add_widget(self.tempLayout)
    
    # 버튼 클릭시 하위 화장기법 선택
    def facepart_selected(self, instance):
        if not self.btn_pressed:
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
    def __init__(self, makeup_types=["shadow", "mascara", "eyeliner"], **kwargs):
        super(SelectMakeUpType, self).__init__(**kwargs)
        self.orientation="vertical"
        self.size_hint=(1, None)
        self.makeup_types = makeup_types
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
        self.selectBrushType = SelectBrushType()
        self.btn_pressed=False
        self.btn = Button(text=self.makeup_type, size_hint_y=None, height=60)
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
    def __init__(self, **kwargs):
        super(SelectBrushType, self).__init__(**kwargs)
        self.orientation="horizontal"
        self.button_pressed=False
        self.selectColor = SelectColor()
        self.button1 = Button(text="1")
        self.button2 = Button(text="2")
        self.button3 = Button(text="3")

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
        self.paintWidget = self.main_layout.imageLayout.paintWidget.brush_size=int(instance.text)
        self.guidelayout = self.main_layout.interfaceLayout.guidelayout
        if self.guidelayout.guide_type != 'color':
            self.guidelayout.add_widget(self.guidelayout.selectColor)
            self.guidelayout.guide_type = 'color'
        """ else:
            self.guidelayout.remove_widget(self.guidelayout.selectColor)
            self.button_pressed=False """
        

class SelectColor(GridLayout):
    def __init__(self, **kwargs):
        super(SelectColor, self).__init__(**kwargs)
        self.cols=2
        colors = ['Blue', 'Red', 'Green', 'White']
        color_buttons = []
        for color in colors:
            btn = Button(text=color)
            btn.bind(on_press=self.color_selected)
            self.add_widget(btn)
            color_buttons.append(btn)

    def color_selected(self, instance):
        main_layout = self
        for i in range(3):
            main_layout = main_layout.parent
        self.main_layout = main_layout
        self.paintWidget = self.main_layout.imageLayout.paintWidget
        print(self.paintWidget.size)
        print(self.paintWidget.canvas)
        if instance.text=="Blue":
            self.paintWidget.color=(0, 0, 1, 0.6)
        elif instance.text=="Red":
            self.paintWidget.color=(1, 0, 0, 0.6)
        elif instance.text=="Green":
            self.paintWidget.color=(0, 1, 0, 0.6)

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
        return MainLayout()


if __name__ == '__main__':
    GuideLineApp().run()