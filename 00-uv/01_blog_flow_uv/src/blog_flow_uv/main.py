#!/usr/bin/env python

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from blog_flow_uv.crews.research_crew.research_crew import ResearchCrew
from blog_flow_uv.crews.writer_crew.writer_crew import WriterCrew


class BlogState(BaseModel):
    sentence_count: int = 0
    topic: str = ""
    blog: str = ""


class BlogFlow(Flow[BlogState]):
    print("BlogFlow")

    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = 50
        self.state.topic = "THE FUTURE OF AI"
    
    @listen(generate_sentence_count)
    def research_blog(self):
        print("Researching blog")
        result = (
            ResearchCrew()
            .crew() 
            .kickoff(inputs={"topic": self.state.topic})
        )

        print("Blog researched", result.raw)
        self.state.blog = result.raw
    

    @listen(generate_sentence_count)
    def generate_blog(self):
        print("Generating blog")
        result = (
            WriterCrew()
            .crew()
            .kickoff(inputs={"topic": self.state.topic, "sentence_count": self.state.sentence_count})
        )

        print("Blog generated", result.raw)
        self.state.blog = result.raw

    @listen(generate_blog)
    def save_blog(self):
        print("Saving blog")
        with open("blog.md", "w") as f:
            f.write(self.state.blog)


def blog_kickoff1():
    print("BlogFlow")

    blog_flow = BlogFlow()
    blog_flow.kickoff()


# def plot():
#     blog_flow = BlogFlow()
#     blog_flow.plot()


if __name__ == "__main__":
    blog_kickoff1()
