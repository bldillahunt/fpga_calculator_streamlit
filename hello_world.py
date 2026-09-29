from nicegui import ui

def press(key):
    print(f'Pressed: {key}')

with ui.row().classes('w-64 mx-auto'):
    with ui.grid(columns=3).classes('gap-2'):
        for label in ['1','2','3','4','5','6','7','8','9','0','.','C']:
            ui.button(label, on_click=lambda e, l=label: press(l)).classes('h-16 text-xl')

ui.run()
