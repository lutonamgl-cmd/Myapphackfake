import os
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
BG_IMAGE_PATH = os.path.join(CURR_DIR, "15050.png")

NEON_GREEN = "#00FF00"
WHITE = "#FFFFFF"
RAINBOW_COLORS = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"]


class BackgroundScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            
            self.bg_tint = Color(1, 1, 1, 1, mode='rgb')
            
            if os.path.exists(BG_IMAGE_PATH):
                self.bg_rect = Rectangle(source=BG_IMAGE_PATH, pos=self.pos, size=self.size)
            else:
                Color(0, 0.03, 0, 1)
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
                
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class CustomHackerButton(Button):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0.75)
        self.color = get_color_from_hex(NEON_GREEN)
        self.font_size = '24sp'
        self.font_name = 'Roboto'
        self.italic = True
        self.bold = True
        self.bind(pos=self.draw_border, size=self.draw_border)

    def draw_border(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0, 1, 0, 1)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=2.5)


class MainMenu(BackgroundScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        button_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 0.25), spacing=30)
        
        self.start_btn = CustomHackerButton(text="Start")
        self.start_btn.bind(on_release=self.go_to_terminal)
        
        self.settings_btn = CustomHackerButton(text="Settings")
        self.settings_btn.bind(on_release=self.go_to_settings)
        
        button_layout.add_widget(self.start_btn)
        button_layout.add_widget(self.settings_btn)
        
        anchor.add_widget(button_layout)
        self.add_widget(anchor)

    def go_to_terminal(self, instance):
        self.manager.current = 'terminal'

    def go_to_settings(self, instance):
        self.manager.current = 'settings'


class TerminalScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rainbow_mode = False
        self.rainbow_index = 0
        self.hue_value = 0.0
        
        from kivy.uix.floatlayout import FloatLayout
        self.main_layout = FloatLayout()

        self.code_label = Label(
            text="", 
            font_size='16sp',
            halign='left', 
            valign='top',
            size_hint=(0.95, 0.85),
            pos_hint={'x': 0.025, 'y': 0.12},
            color=get_color_from_hex(NEON_GREEN)
        )
        self.code_label.bind(size=self.code_label.setter('text_size'))
        self.main_layout.add_widget(self.code_label)
     
        self.secret_btn = Button(
            size_hint=(None, None),
            size=('60dp', '60dp'),
            pos_hint={'right': 1, 'top': 1},
            background_color=(0, 0, 0, 0)
        )
        self.secret_btn.bind(on_release=self.toggle_rainbow)
        self.main_layout.add_widget(self.secret_btn)
        
        back_btn = Button(
            text="< MENU",
            size_hint=(None, None),
            size=('90dp', '40dp'),
            pos_hint={'x': 0.05, 'y': 0.03},
            background_color=get_color_from_hex("#111111"),
            color=get_color_from_hex(WHITE)
        )
        back_btn.bind(on_release=self.go_back)
        self.main_layout.add_widget(back_btn)
        
        self.add_widget(self.main_layout)
        Window.bind(on_keydown=self.on_key_down)
        
    def generate_fake_code(self):
        app = App.get_running_app()
        code_type = app.code_style
        
        if code_type == "Binary":
            return "".join(random.choice(["0", "1", " ", "\n"]) for _ in range(50))
        elif code_type == "Hexadecimal":
            hex_chars = "0123456789ABCDEF \n"
            return "0x" + "".join(random.choice(hex_chars) for _ in range(40))
        elif code_type == "Matrix Python":
            snippets = [
                "import security, database\n", "if database.is_locked():\n",
                "    bypass_firewall()\n", "def inject_payload():\n",
                "    return system_override()\n", "try:\n    force_access()\n",
                "except Exception:\n    pass\n", "CONNECTING TO SERVER...\n"
            ]
            return random.choice(snippets)
        return "1010"

    def handle_input(self):
        new_code = self.generate_fake_code()
        current_text = self.code_label.text
        if len(current_text) > 1000:
            current_text = current_text[-600:]
        self.code_label.text = current_text + "\n" + new_code

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if self.manager.current == 'terminal':
            self.handle_input()
            return True
        return False
        
    def on_touch_down(self, touch):
        if self.manager.current == 'terminal' and not self.secret_btn.collide_point(*touch.pos):
            self.handle_input()
        return super().on_touch_down(touch)

    def toggle_rainbow(self, instance):
        self.rainbow_mode = not self.rainbow_mode
        
        if self.rainbow_mode:
            self.code_label.text += "\n\n!!! RAINBOW MODE ACTIVATED !!!\n\n"
            
            Clock.schedule_interval(self.update_rainbow_color, 0.08)
            Clock.schedule_interval(self.update_rainbow_bg, 1.0 / 40.0)
        else:
            
            Clock.unschedule(self.update_rainbow_color)
            Clock.unschedule(self.update_rainbow_bg)
            
           
            self.bg_tint.mode = 'rgb'
            self.bg_tint.rgba = (1, 1, 1, 1)
            
            
            app = App.get_running_app()
            self.code_label.color = get_color_from_hex(app.terminal_color)

    def update_rainbow_color(self, dt):
        if not self.rainbow_mode:
            return False
        color_hex = RAINBOW_COLORS[self.rainbow_index]
        self.code_label.color = get_color_from_hex(color_hex)
        self.rainbow_index = (self.rainbow_index + 1) % len(RAINBOW_COLORS)

    def update_rainbow_bg(self, dt):
        if not self.rainbow_mode:
            return False
        
        self.hue_value += 0.005
        if self.hue_value > 1.0:
            self.hue_value = 0.0
            
        
        self.bg_tint.mode = 'hsv'
        self.bg_tint.hsv = (self.hue_value, 0.85, 0.9)

    def go_back(self, instance):
        if self.rainbow_mode:
            self.toggle_rainbow(None)
        self.manager.current = 'menu'


class SettingsScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        layout.add_widget(Label(text="SETTINGS", font_size='28sp', color=get_color_from_hex(NEON_GREEN), size_hint_y=0.15))
        
        layout.add_widget(Label(text="Select Code Style:", size_hint_y=0.05))
        self.style_spinner = Spinner(
            text="Binary",
            values=("Binary", "Hexadecimal", "Matrix Python"),
            background_color=get_color_from_hex("#111111"),
            size_hint_y=0.1
        )
        self.style_spinner.bind(text=self.change_style)
        layout.add_widget(self.style_spinner)
        
        layout.add_widget(Label(text="Select Code Base Color:", size_hint_y=0.05))
        self.color_spinner = Spinner(
            text="Green",
            values=("Green", "White", "Amber/Orange"),
            background_color=get_color_from_hex("#111111"),
            size_hint_y=0.1
        )
        self.color_spinner.bind(text=self.change_color)
        layout.add_widget(self.color_spinner)
        
        layout.add_widget(Label(text="(Note: Color selection will not alter active Rainbow Mode)", font_size='12sp', size_hint_y=0.1))
        
        back_btn = Button(text="Save & Close", background_color=get_color_from_hex("#441111"), size_hint_y=0.12)
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
    def change_style(self, spinner, text):
        App.get_running_app().code_style = text
        
    def change_color(self, spinner, text):
        app = App.get_running_app()
        if text == "Green":
            app.terminal_color = NEON_GREEN
        elif text == "White":
            app.terminal_color = WHITE
        elif text == "Amber/Orange":
            app.terminal_color = "#FFB000"
            
        terminal_screen = self.manager.get_screen('terminal')
        if not terminal_screen.rainbow_mode:
            terminal_screen.code_label.color = get_color_from_hex(app.terminal_color)

    def go_back(self, instance):
        self.manager.current = 'menu'


class HackerApp(App):
    def build(self):
        self.code_style = "Binary"
        self.terminal_color = NEON_GREEN
        
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(TerminalScreen(name='terminal'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm


if __name__ == '__main__':
    HackerApp().run()
