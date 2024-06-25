base = system.import_library('../base.py')
encoding = base.encoding
NLPTasks = base.NLPTasks


async def rag_func(query: str):
    """
    Respond when the person asks about the weather

    Args:
        query: what's the weather like today
     """
    print('mq nlp test query: ', query)
    system.messaging.post('deal_nlp_tasks', [NLPTasks.RAG.encode(encoding), query.encode(encoding)])
