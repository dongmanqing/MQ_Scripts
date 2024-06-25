encoding = 'utf-8'


class NLPTasks:
    RAG = 'RAG'


class ResponseCode:
	KeepSilent = 0
	Success = 1
	Fail = 2


class Config:
    rag_addr = 'tcp://0.0.0.0:6666'  # backed server address

