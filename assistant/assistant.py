import openai
import time
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

class QAAssistant:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        #self.file = self._upload_file(file_path)
        self.assistant = self._create_assistant()
        self.thread = self._create_thread()

    def _upload_file(self, file_path):
        file = self.client.files.create(
            file=open(file_path, "rb"),
            purpose='assistants'
        )
        return file

    def _create_assistant(self):

        return self.client.beta.assistants.retrieve(assistant_id= 'asst_0bwBnAPn9DmKKfZgaxnOYVLB')

    def _create_thread(self):
        return self.client.beta.threads.create()

    def ask_question(self, prompt):
        return input(prompt)

    def run_assistant(self, user_question):
       
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_question
        )

        run = self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.assistant.id)

        run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)
        while run_status.status != "completed":
            time.sleep(2)
            run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)

        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        last_message_for_run = None
        for message in reversed(messages.data):
            if message.role == "assistant" and message.run_id == run.id:
                last_message_for_run = message
                break

        if last_message_for_run:
            response = f"{last_message_for_run.content[0].text.value} \n"
            print(response)
            return response

        