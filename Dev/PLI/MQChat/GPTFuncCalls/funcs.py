"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""

MODE_REACTIVE = 0
MODE_PROACTIVE = 1  # can initiate conversation based on observations
utils = system.import_library('../../../../HB3/Utils.py')


async def switch_to_proactive_chat():
    """
    Proactive chat, enter proactive mode, enter observation mode
    This function will trigger background task and returns immediately

    """
    # utils.start_other_script(system, '../VisualActivities/mq_trigger_vrec_posegen.py')
    utils.stop_other_script(system, '../VisualActivities/mq_trigger_vtasks.py')
    utils.start_other_script(system, '../VisualActivities/mq_trigger_vtasks.py')
    # system.messaging.post('switch_chat_mode', MODE_PROACTIVE)
    # print('call function switch_to_proactive_chat OK!!!')
    system.messaging.post('tts_say', ['enter proactive mode', 'EN'])
    # return "swithed to proactive chat mode."


async def switch_to_reactive_chat():
    """
    Reactive chat, enter reactive mode, exit proactive mode, exit observation mode

    """
    utils.stop_other_script(system, '../VisualActivities/mq_trigger_vrec_posegen.py')
    # system.messaging.post('switch_chat_mode', MODE_REACTIVE)
    print('call function switch_to_reactive_chat OK!!!')
    system.messaging.post('tts_say', ['enter reactive mode', 'EN'])

    # return "switched to reactive chat mode."
