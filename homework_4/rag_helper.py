from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from sqlite import SQLiteSpanExporter

INSTRUCTIONS = '''
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
'''

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}
'''.strip()


provider = TracerProvider()
provider.add_span_processor(
    SimpleSpanProcessor(SQLiteSpanExporter("traces.db"))
)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-zoomcamp")



class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model

    def search(self, query, num_results=5):
        with tracer.start_as_current_span("search") as span:
            span.set_attribute("search.query", query)
            span.set_attribute("search.num_results", num_results)
            results = self.index.search(query, num_results=num_results)
            span.set_attribute("search.results", len(results))
            return results


    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc['filename'])
            lines.append(doc['content'])
            lines.append('')

        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:
            input_messages = [
                {'role': 'developer', 'content': self.instructions},
                {'role': 'user', 'content': prompt}
            ]
            response = self.llm_client.responses.create(
                model=self.model,
                input=input_messages
            )
            span.set_attribute("input_tokens", response.usage.input_tokens)
            span.set_attribute("output_tokens", response.usage.output_tokens)
            span.set_attribute("cost", response.usage.total_tokens * 0.0000015)

            return response

    def rag(self, query):
        with tracer.start_as_current_span("rag") as span:
            span.set_attribute("rag.query", query)
            search_results = self.search(query)
            span.set_attribute("rag.num_results", len(search_results))
            prompt = self.build_prompt(query, search_results)
            response = self.llm(prompt)
            answer = response.output_text
            span.set_attribute("rag.answer", answer)
            return answer
