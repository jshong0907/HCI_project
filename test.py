import os


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
from kivy.uix.image import Image
from subprocess import Popen, PIPE

from beautygan import BeautyGAN


class PopupLayout(Popup):
    def __init__(self, **kwargs):
        super(PopupLayout, self).__init__(**kwargs)


# vertical한 레이아웃
class TempLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(TempLayout, self).__init__(**kwargs)
        self.orientation = "vertical"
        


class GuideLayout(ScrollView):
    def __init__(self, **kwargs):
        super(GuideLayout, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.size=(Window.width, Window.height)
        # self.size_hint=(1, None)
        # self.add_widget(Button(background_normal = '0.png', size_hint=(.9, .9)))
        
            
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def guide_select(self, paths):
        self.add_widget(SelectGuideLayout(paths, size_hint=(1, 1)))
        # for i in paths:
        #    self.add_widget(SelectGuideLayout(i))
        #    break
        # root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        # root.add_widget(self)
            # self.add_widget(Button(background_normal = i, size_hint=(.9, .9)))
        

class SelectGuideLayout(GridLayout):
    def __init__(self, paths, **kwargs):
        super(SelectGuideLayout, self).__init__(**kwargs)
        #self.rows=len(paths)
        self.cols=1
        self.spacing=10
        self.size_hint_y=None
        self.bind(minimum_height=self.setter('height'))
        # self.orientation = 'vertical'
        self.paths = paths
        idx = 0
        for path in self.paths:  
            guideline = Button(background_normal=path, size_hint=(1, None), size=(self.size[0], self.size[0]), border=(0,0,0,0))
            guideline.bind(on_press=self.guideimg_seleted)
            self.add_widget(guideline)
            idx += 1

    def guideimg_seleted(self, instance):
        print(instance.background_normal)
        # pop = PopupLayout(title='guideline', content=Image(source=instance.background_normal), size_hint=(None, None), size=(400, 400))
        # pop.open()

        Popen(['python', 'guide.py', '--path', instance.background_normal], shell=True)
        


            # self.add_widget(Button(background_normal=path, size_hint=(1, None), size=(self.size[0], self.size[0]), border=(0,0,0,0)))  

            #size = self.size[0], self.size[0]
            # self.add_widget(Button(background_normal = i, size_hint=(1, None)))
        
        # self.add_widget(Button(background_normal = self.path, size_hint=(.9, .9)))
        


# default scrollview
class TempScroll(ScrollView):
    def __init__(self, **kwargs):
        super(TempScroll, self).__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.orientation = "horizontal"
        self.padding = [10, 10, 10, 10]
        self.spacing = 10
        self.add_widget(ImageLayout(size_hint=(.6, 1)))
        self.add_widget(InterfaceLayout(size_hint=(.4, 1)))


# 시작 시 좌측 이미지 출력
class ImageLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ImageLayout, self).__init__(**kwargs)
        self.spacing = 10
        self.paintWidget = PaintWidget()
        self.add_widget(self.paintWidget)

        with self.canvas.before:
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
            self.rect.source = "imgs/no_makeup/vSYYZ639.png"
            
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

# color를 parameter로 받는 그리기 위젯
class PaintWidget(Widget):
    def __init__(self, color=(0, 0, 0, 1), **kwargs):
        super(PaintWidget, self).__init__(**kwargs)
        self.color = color

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*self.color)
            d = 10
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=2)
            
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
        self.bg = BeautyGAN()
        super(MakeupLayout, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        # 화장기법 및 브러쉬 선택
        self.add_widget(SelectMakeUp(size_hint=(1, .8)))
        # 가이드라인 선택 버튼
        guideline = Button(text='Guideline', size_hint=(1, .2))
        guideline.bind(on_press=self.guideline_seleted)
        self.add_widget(guideline)
    
    def guideline_seleted(self, instance):

        paths = self.bg.run('imgs/no_makeup/vSYYZ639.png')
        interface = self.parent
        guidelayout = interface.guidelayout
        
        guidelayout.guide_select(paths)
            



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
        self.makeup_type_buttons = []
        self.makeup_type_layouts  = []
        for makeup_type in makeup_types:
            btn = Button(text=makeup_type, size_hint_y=None, height=60)
            layout = TempLayout(orientation="vertical", size_hint_y=None, height=60)
            layout.add_widget(btn)
            self.makeup_type_buttons.append(btn)
            self.makeup_type_layouts.append(layout)
        for makeup_type_layout in self.makeup_type_layouts:
            self.add_widget(makeup_type_layout)

    def makeuptype_selected(self, instace):
        pass
        
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