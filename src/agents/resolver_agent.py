from src.resolver_dispatcher import dispatch

class ResolverAgent:
    def process(self, session, triage_result):
        return dispatch(session, triage_result)
