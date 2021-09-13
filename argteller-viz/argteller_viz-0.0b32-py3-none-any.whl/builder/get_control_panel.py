from ..widgets.dynamic_switch import DynamicSwitch

try:

    from IPython.display import display
    import ipywidgets as widgets
    from ipywidgets import HBox, Label, VBox
    from ipywidgets import Button, Layout, HTML

except ModuleNotFoundError:

    pass

def get_control_panel(access_object):

    def on_update_topic_choice(*args):

        tab_children = []

        for idx, topic_name in enumerate(topic_choice.value):

            vbox = access_object.param_vboxes[topic_name]
            
            tab.set_title(idx, topic_name)
            tab_children.append(vbox)

        tab.children = tab_children
    
    style = style = {'description_width': 'initial'}

    topics = access_object.get_topics()

    topic_choice = widgets.SelectMultiple(
        options=topics,
        value=topics,
        rows=len(topics) + 1,
        disabled=False,
        style=style
    )

    label = widgets.Label(value='Select modes (keep shift and/or ctrl (or command) pressed)')

    topic_choice_box = VBox()
    topic_choice_box.children = [label, topic_choice]

    
    tab = widgets.Tab()

    tab_box = VBox()
    tab_box.children = [tab]
    
    topic_choice.observe(on_update_topic_choice)
    
    tab_children = []

    for idx, topic_name in enumerate(topic_choice.value):

        vbox = access_object.param_vboxes[topic_name]

        tab.set_title(idx, topic_name)
        tab_children.append(vbox)

    tab.children = tab_children

    access_object.tab_widget = tab
    access_object.topic_choice_widget = topic_choice
    
    v = DynamicSwitch(topic_choice_box, tab_box, access_object)





    
    return v

