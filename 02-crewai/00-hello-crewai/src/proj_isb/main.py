
from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from litellm import completion


class ExampleFlow(Flow):
    model = "gpt-4o-mini"

    @start()
    def generate_city(self):
        print("Starting flow")
        # Each flow state automatically gets a unique ID
        print(f"Flow State ID: {self.state['id']}")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "Return the name of a random city in the world.",
                },
            ],
        )

        random_city = response["choices"][0]["message"]["content"]
        # Store the city in our state
        self.state["city"] = random_city
        print(f"Random City: {random_city}")

        return random_city

    @listen(generate_city)
    def generate_fun_fact(self, random_city):
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Tell me a fun fact about {random_city}",
                },
            ],
        )

        fun_fact = response["choices"][0]["message"]["content"]
        # Store the fun fact in our state
        self.state["fun_fact"] = fun_fact
        return fun_fact


def kickoff():
    flow = ExampleFlow()
    result = flow.kickoff()

    print(f"Generated fun fact: {result}")

# #!/usr/bin/env python
# from random import randint

# from pydantic import BaseModel

# from crewai.flow import Flow, listen, start

# from proj_isb.crews.poem_crew.poem_crew import PoemCrew


# class PoemState(BaseModel):
#     sentence_count: int = 1
#     poem: str = ""


# class PoemFlow(Flow[PoemState]):

#     @start()
#     def generate_sentence_count(self):
#         print("Generating sentence count")
#         self.state.sentence_count = randint(1, 5)

#     @listen(generate_sentence_count)
#     def generate_poem(self):
#         print("Generating poem")
#         result = (
#             PoemCrew()
#             .crew()
#             .kickoff(inputs={"sentence_count": self.state.sentence_count})
#         )

#         print("Poem generated", result.raw)
#         self.state.poem = result.raw

#     @listen(generate_poem)
#     def save_poem(self):
#         print("Saving poem")
#         with open("poem.txt", "w") as f:
#             f.write(self.state.poem)


# def kickoff():
#     poem_flow = PoemFlow()
#     poem_flow.kickoff()

# def plot():
#     poem_flow = PoemFlow()
#     poem_flow.plot()


# if __name__ == "__main__":
#     kickoff()
